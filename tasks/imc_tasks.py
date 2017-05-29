# -*- coding: utf-8 -*-

import os
import json
import random

from imc.tasks.services.efg_xmlparser import EFG_XMLParser
# from imc.tasks.services.fhg_xmlparser import FHG_XMLParser
from imc.tasks.services.creation_repository import CreationRepository
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.models.neo4j import (
    Shot
)

from rapydo.basher import BashCommands
from rapydo.utils.logs import get_logger
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations

from flask_ext.flask_celery import CeleryExt

celery_app = CeleryExt.celery_app

log = get_logger(__name__)


####################
# Define your celery tasks

def progress(self, state, info):
    if info is not None:
        log.debug("%s [%s]" % (state, info))
    self.update_state(state=state)


@celery_app.task(bind=True)
def import_file(self, path, resource_id, mode):
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
                analyze_path = '/uploads/Analize/' + \
                    group.uuid + '/' + video_filename.split('.')[0] + '/'
                log.debug('analyze path: {0}'.format(analyze_path))

                progress(self, 'Executing automatic tools', path)
                params = []
                params.append("/code/imc/scripts/analysis/analyze.py")
                if mode is not None:
                    log.info('Analyze with mode [%s]' % mode)
                    params.append('-' + mode)
                params.append(video_path)
                bash = BashCommands()
                try:
                    output = bash.execute_command(
                        "python3",
                        params,
                        parseException=True
                    )
                    log.info(output)

                except BaseException as e:
                    log.error(e)
                    video_node.status = 'ERROR'
                    video_node.status_message = str(e)
                    video_node.save()
                    raise(e)

                # SAVE AUTOMATIC ANNOTATIONS
                progress(self, 'Extracting automatic annotations', path)

                extract_tech_info(self, item_node, analyze_path)

                # FIXME naive filter
                # find TVS annotations with this item as target
                annotations = item_node.targeting_annotations.all()
                if annotations is not None:
                    repo = AnnotationRepository(self.graph)
                    # here we expect ONLY one anno if present
                    for anno in annotations:
                        if anno.annotation_type == 'TVS':
                            anno_id = anno.id
                            log.debug(anno)
                            repo.delete_tvs_annotation(anno)
                            log.info(
                                "Deleted existing TVS annotation [%s]"
                                % anno_id)

                extract_tvs_annotation(self, item_node, analyze_path)

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


def extract_tech_info(self, item, analyze_dir_path):
    """
    Extract technical information about the given content from result file
    origin_info.json and save them as Item properties in the database.
    """
    if not os.path.exists(analyze_dir_path):
        raise IOError(
            "Analyze results does not exist in the path %s", analyze_dir_path)
    # check for info result
    tech_info_filename = 'transcoded_info.json'  # 'origin_info.json'
    tech_info_path = os.path.join(
        os.path.dirname(analyze_dir_path), tech_info_filename)
    if not os.path.exists(tech_info_path):
        log.warning("Info tech CANNOT be extracted: [%s] does not exist",
                    tech_info_path)
        return

    # load info from json
    with open(tech_info_path) as data_file:
        data = json.load(data_file)

    # FIXME to get the thumbnail assigned to a given AV digital object?
    # thumbnail
    thumbnails_uri = os.path.join(analyze_dir_path, 'thumbs/')
    item.thumbnail = get_thumbnail(thumbnails_uri)
    # duration
    item.duration = data["streams"][0]["duration"]
    # framerate
    item.framerate = data["streams"][0]["avg_frame_rate"]
    # dimension
    item.dimension = data["format"]["size"]
    # format
    item.digital_format = [None for _ in range(4)]
    # container: e.g."AVI", "MP4", "3GP"
    item.digital_format[0] = data["format"]["format_name"]
    # coding: e.g. "WMA","WMV", "MPEG-4", "RealVideo"
    item.digital_format[1] = data["streams"][0]["codec_long_name"]
    # format: RFC 2049 MIME types, e.g. "image/jpg", etc.
    item.digital_format[2] = data["format"]["format_long_name"]
    # resolution: The degree of sharpness of the digital object expressed in
    # lines or pixel
    item.digital_format[3] = data["format"]["bit_rate"]

    item.uri = data["format"]["filename"]
    if item.item_type == 'Video':
        # summary
        summary_filename = 'summary.jpg'
        summary_path = os.path.join(
            os.path.dirname(analyze_dir_path), summary_filename)
        if not os.path.exists(summary_path):
            log.warning("{0} CANNOT be found in the path: [{1}]".format(
                        summary_filename, analyze_dir_path))
        else:
            item.summary = summary_path
    item.save()

    log.info('Extraction of techincal info completed')


def get_thumbnail(path):
    """
    Returns a random filename, chosen among the jpg files of the given pat.h
    """
    jpg_files = [f for f in os.listdir(path) if f.endswith('.jpg')]
    index = random.randrange(0, len(jpg_files))
    return os.path.join(
        os.path.dirname(path), jpg_files[index])


def extract_tvs_annotation(self, item, analyze_dir_path):
    """
    Extract temporal video segmentation results from storyboard.json file and
    save them as Annotation in the database.
    """
    tvs_dir_path = os.path.join(analyze_dir_path, 'storyboard/')
    if not os.path.exists(tvs_dir_path):
        raise IOError(
            "Storyboard directory does not exist in the path %s", tvs_dir_path)
    # check for info result
    tvs_filename = 'storyboard.json'
    tvs_path = os.path.join(
        os.path.dirname(tvs_dir_path), tvs_filename)
    if not os.path.exists(tvs_path):
        raise IOError(
            "Shots CANNOT be extracted: [%s] does not exist", tvs_path)

    log.debug('get shots from file [%s]' % tvs_path)

    # load info from json
    with open(tvs_path) as data_file:
        data = json.load(data_file)

    shots = []
    for s in data['shots']:
        log.debug(s)
        shot = Shot()
        shot.shot_num = s['shot_num']
        shot.start_frame_idx = s['frame']
        shot.timestamp = s['timecode']
        try:
            shot.duration = s['len']
        except ValueError:
            log.warning("Invalid duration in the shot {0} \
                for value '{1}'".format(shot.shot_num, s['len']))
            shot.duration = None

        shot.thumbnail_uri = os.path.join(tvs_dir_path, s['img'])
        shots.append(shot)

    if len(shots) == 0:
        log.warning("Shots CANNOT be found in the file [%s]" % tvs_path)
        return

    # Save Shots in the database
    repo = AnnotationRepository(self.graph)
    repo.create_tvs_annotation(item, shots)

    log.info('Extraction of TVS info completed')
