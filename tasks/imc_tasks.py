# -*- coding: utf-8 -*-

from restapi.resources.basher import BashCommands
from ...services.celery import celery_app
from commons.logs import get_logger
from restapi.resources.services.neo4j.graph_endpoints import \
    GraphBaseOperations
import os
# from lxml import etree
from .services.efg_xmlparser import EFG_XMLParser
from .services.creation_repository import CreationRepository
# import xml.etree.ElementTree as ET

log = get_logger(__name__)


####################
# Define your celery tasks

def progress(self, state, info):
    if info is not None:
        log.debug("%s [%s]" % (state, info))
    self.update_state(state=state)


@celery_app.task(bind=True)
def import_file(self, path, resource_id):
    with celery_app.app.app_context():

        progress(self, 'Starting import', path)

        self.graph = celery_app.get_service('neo4j')

        xml_resource = None
        try:

            xml_resource = self.graph.Stage.nodes.get(uuid=resource_id)

            group = GraphBaseOperations.getSingleLinkedNode(
                xml_resource.ownership)

            # METADATA EXTRACTION
            filename, file_extension = os.path.splitext(path)

            if file_extension.startswith("."):
                file_extension = file_extension[1:]

            progress(self, 'Extracting descriptive metadata', path)

            videos = extract_av_creation_refs(self, path)
            if (videos is None):
                raise Exception(
                    "No video match found importing file %s" % path)

            for video_filename in videos:

                if video_filename is None:
                    log.warning("Why the video filename is None??")
                    continue

                log.info("Video filename %s", video_filename)

                # TO FIX: will be something like: root + video_filename ?
                # root = basedir(path) ?
                video_path = os.path.join(
                    os.path.dirname(path), video_filename)
                if not os.path.exists(video_path):
                    log.warning(
                        "Video content does not exist in the path %s",
                        video_path)
                    continue

                log.debug('filename [%s], extension [%s]' %
                          (filename, file_extension))

                # Creating video resource
                properties = {}
                properties['filename'] = video_filename
                properties['path'] = video_path

                try:
                    # This is a task restart? What to do in this case?
                    video_node = self.graph.Stage.nodes.get(**properties)
                    log.debug("Video resource already exist for %s" %
                              video_path)
                except self.graph.Stage.DoesNotExist:
                    video_node = self.graph.Stage(**properties).save()
                    video_node.ownership.connect(group)
                    log.debug("Video resource created for %s" % video_path)

                video_node.status = "IMPORTING"
                # TO FIX: video analysis will be a new tasks
                # task = analyze_video.apply_async(
                #     args=[path, video_node.uuid],
                #     countdown=20
                # )
                # video_node.task_id = task.id
                video_node.save()

                # check for existing item
                if len(video_node.item.all()) > 0:
                    log.debug("Item already exists for Stage[%s]" % video_path)
                    item_node = video_node.item.single()
                else:
                    # Extract metadata item and creation
                    item_properties = {}
                    item_properties['item_type'] = "Video"  # FIXME
                    item_node = self.graph.Item(**item_properties).save()
                    item_node.ownership.connect(group)
                    item_node.meta_source.connect(xml_resource)
                    item_node.content_source.connect(video_node)
                    item_node.save()
                    log.debug("Item resource created")

                extract_descriptive_metadata(
                    self, path, video_filename, item_node)

                # EXECUTE AUTOMATC TOOLS
                progress(self, 'Executing automatic tools', path)
                params = []
                params.append("/imedia-pipeline-cin/analyze.py")
                params.append(video_filename)
                # bash = BashCommands()
                # try:
                #     output = bash.execute_command(
                #         "python3",
                #         params,
                #         parseException=True
                #     )
                #     log.info(output)

                # except BaseException as e:
                #     log.error(e)
                #     video_node.status = 'ERROR'
                #     video_node.status_message = str(e)
                #     video_node.save()
                #     raise(e)

                # SAVE AUTOMATIC ANNOTATIONS
                progress(self, 'Extracting automatic annotations', path)
                # TODO
                video_node.status = 'COMPLETED'
                video_node.status_message = 'Nothing to declare'
                video_node.save()

                # TO FIX: move video in the datadir
                # os.rename(video_path, datadir/video_node.uuid)

            xml_resource.status = 'COMPLETED'
            xml_resource.status_message = 'Nothing to declare'
            xml_resource.save()

            progress(self, 'Completed', path)
            # os.remove(path)

        # except self.graph.File.DoesNotExist:
        #     progress(self, 'Import error', None)
        #     log.error("Task error, path %s not found" % path)
        except Exception as e:
            progress(self, 'Import error', None)
            log.error("Task error, %s" % e)
            if xml_resource is not None:
                xml_resource.status = 'ERROR'
                xml_resource.status_message = str(e)
                xml_resource.save()
            raise e

        return 1


def extract_av_creation_refs(self, path):
    """
    Extract the list of references from the incoming XML file.
    """
    videos = []

    parser = EFG_XMLParser()

    av_creations = parser.get_av_creations(path)
    for av_creation in av_creations:
        video = parser.get_av_creation_ref(av_creation)
        if video is None:
            log.debug("No video ref found")
            continue
        # log.debug(ET.tostring(av_creation, encoding='UTF-8'))
        # log.debug(EFG_XMLParser.prettify(av_creation))
        videos.append(video)

    # This will be a list of video extracted from XML file
    log.debug('[%s]' % ', '.join(map(str, videos)))
    return videos


def extract_descriptive_metadata(self, path, item_ref, item_node):
    """
    Simple metadata ingestion:
      - validate against EFG-XSD schema
      - look for the record with the filename in ref elem
      - bind the model
      - save the model (if an occurrence with the same id already exists,
        delete the old item?)
      - return the referred video filename
    notes:
      - only EFG xml file allowed
      - lookup at the first occurence of the item in the stage area,
        ignoring the rest
      - raise exception whenever those conditions are not met
    """
    # import codecs
    # with codecs.open(path, 'r', encoding='utf8') as f:
    # #with codecs.open(path, 'r', encoding='latin-1') as f:
    #     while True:
    #         line = f.readline()
    #         if not line:
    #             break
    #         #log.info(line.strip())
    if item_node.item_type != 'Video':
        raise Exception('Parsing NON AudioVisual not yet implemented')

    parser = EFG_XMLParser()
    record = parser.get_av_creation_by_ref(path, item_ref)
    # log.debug(EFG_XMLParser.prettify(record))
    if record is None:
        raise Exception('Record instance cannot be None')

    # Creating AV_Entity
    av_creation = parser.parse_av_creation(record)
    repo = CreationRepository(self.graph)
    repo.create_av_entity(
        av_creation['properties'],
        item_node,
        av_creation['relationships']['titles'],
        av_creation['relationships']['keywords'],
        av_creation['relationships']['descriptions'])
    # log.info('Identifying Title: %s' % parser.get_identifying_title(record))


def extract_automatic_annotation(self, path):
    """ """
    # tree = etree.parse(path)
    # log.debug(etree.tostring(tree, pretty_print=True))
    pass
