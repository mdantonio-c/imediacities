# -*- coding: utf-8 -*-

import os
import json
import random

from imc.tasks.services.efg_xmlparser import EFG_XMLParser
from imc.tasks.services.creation_repository import CreationRepository
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.models.neo4j import Shot
from imc.models import codelists

# from imc.analysis.fhg import FHG
from scripts.analysis.analyze import make_movie_analize_folder, analize

# from restapi.basher import BashCommands
from utilities.logs import get_logger
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations

from restapi.flask_ext.flask_celery import CeleryExt

celery_app = CeleryExt.celery_app

log = get_logger(__name__)


####################
# Define your celery tasks

def progress(self, state, info):
    if info is not None:
        log.info("%s [%s]" % (state, info))
    self.update_state(state=state)


@celery_app.task(bind=True)
def import_file(self, path, resource_id, mode):
    with celery_app.app.app_context():

        progress(self, 'Starting import', path)

        self.graph = celery_app.get_service('neo4j')

        xml_resource = None
        try:
            xml_resource = self.graph.MetaStage.nodes.get(uuid=resource_id)

            group = GraphBaseOperations.getSingleLinkedNode(
                xml_resource.ownership)

            # METADATA EXTRACTION
            filename, file_extension = os.path.splitext(path)

            if file_extension.startswith("."):
                file_extension = file_extension[1:]

            log.debug('filename [{0}], extension [{1}]'.format(
                filename, file_extension))

            progress(self, 'Extracting descriptive metadata', path)

            source_id = extract_creation_ref(self, path)
            if source_id is None:
                raise Exception(
                    "No source ID found importing metadata file %s" % path)
            item_type = extract_item_type(self, path)
            if codelists.fromCode(item_type, codelists.CONTENT_TYPES) is None:
                raise Exception("Invalid content type for: " + item_type)
            log.info("Content source ID: {0}; TYPE: {1}".format(
                source_id, item_type))

            # check for existing item
            item_node = xml_resource.item.single()
            # if item_node is not None:
            #     log.debug("Item already exists for metadata Stage[%s]" % path)
            #     item_node = xml_resource.item.single()
            # else:
            if item_node is None:
                item_properties = {}
                item_properties['item_type'] = item_type
                item_node = self.graph.Item(**item_properties).save()
                item_node.ownership.connect(group)
                item_node.meta_source.connect(xml_resource)
                item_node.save()
                log.debug("Item resource created")

            extract_descriptive_metadata(
                self, path, item_type, item_node)

            # To ensure that the content item and its metadata will be
            # correctly linked in the system and its repositories,
            # FHI-Partners are expected to name the content item file,
            # using the following method:
            # The FHI project acronym_the FHI content ID (this is the
            # Content item ID in the local FHI’s database).
            # For example: CRB_1234.mp4
            basedir = os.path.dirname(os.path.abspath(path))
            log.debug("Content basedir {0}".format(basedir))
            content_path, content_filename = lookup_content(
                self, basedir, source_id)

            content_node = None
            if content_path is not None:
                # Create content resource
                properties = {}
                properties['filename'] = content_filename
                properties['path'] = content_path

                try:
                    # This is a task restart? What to do in this case?
                    content_node = self.graph.ContentStage.nodes.get(**properties)
                    log.debug("Content resource already exist for %s" % content_path)
                except self.graph.ContentStage.DoesNotExist:
                    content_node = self.graph.ContentStage(**properties).save()
                    content_node.ownership.connect(group)
                    # connect the item to the content source
                    item_node.content_source.connect(content_node)
                    log.debug("Content resource created for %s" % content_path)

            fast = False
            if mode is not None:
                mode = mode.lower()
                if mode == 'skip':
                    log.info('Analyze skipped for source id: ' + source_id)
                    xml_resource.status = 'COMPLETED'
                    xml_resource.status_message = 'Nothing to declare'
                    xml_resource.save()
                    # content_node.status = 'SKIPPED'
                    # content_node.status_message = 'Nothing to declare'
                    # content_node.save()
                    return 1
                fast = (mode == 'fast')

            if content_node is None:
                raise Exception(
                    "Pipeline cannot be started: \
                    content does not exist in the path {0} for source ID {1}"
                    .format(content_path, source_id))

            content_node.status = "IMPORTING"
            # TO FIX: video analysis will be a new tasks
            # task = analyze_video.apply_async(
            #     args=[path, video_node.uuid],
            #     countdown=20
            # )
            # video_node.task_id = task.id
            content_node.save()

            # EXECUTE AUTOMATC TOOLS

            # workflow = FHG(video_path, "/uploads")
            # workflow.analyze(fast)

            movie = os.path.join('/uploads', content_path)
            if not os.path.exists(movie):
                raise Exception('Bad input file', movie)

            out_folder = make_movie_analize_folder(movie)
            if out_folder == "":
                raise Exception('Failed to create out_folder')

            log.info("Analize " + movie)

            if analize(movie, out_folder, fast):
                log.info('Analize done')
            else:
                log.error('Analize terminated with errors')

            # params = []
            # params.append("/code/scripts/analysis/analyze.py")
            # if mode is not None:
            #     log.info('Analyze with mode [%s]' % mode)
            #     params.append('-%s' % mode)
            # params.append(video_path)

            # progress(self, 'Executing automatic tools', path)
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

            # REMOVE ME!!
            # video_node.status = 'ERROR'
            # video_node.status_message = "STOP ME"
            # video_node.save()

            analyze_path = '/uploads/Analize/' + \
                group.uuid + '/' + content_filename.split('.')[0] + '/'
            log.debug('analyze path: {0}'.format(analyze_path))

            # SAVE AUTOMATIC ANNOTATIONS
            progress(self, 'Extracting automatic annotations', path)

            extract_tech_info(self, item_node, analyze_path)

            # FIXME naive filter
            # find TVS and VQ annotations with this item as source
            annotations = item_node.sourcing_annotations.all()
            if annotations is not None:
                repo = AnnotationRepository(self.graph)
                # here we expect ONLY one anno if present
                for anno in annotations:
                    anno_id = anno.id
                    if anno.annotation_type == 'TVS':
                        log.debug(anno)
                        repo.delete_tvs_annotation(anno)
                        log.info(
                            "Deleted existing TVS annotation [%s]"
                            % anno_id)
                    elif anno.annotation_type == 'VIM':
                        log.debug(anno)
                        repo.delete_vim_annotation(anno)
                        log.info(
                            "Deleted existing VIM annotation [%s]"
                            % anno_id)

            extract_tvs_vim_annotations(self, item_node, analyze_path)

            # TODO
            content_node.status = 'COMPLETED'
            content_node.status_message = 'Nothing to declare'
            content_node.save()

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


def extract_creation_ref(self, path):
    """
    Extract the source id reference from the incoming XML file.
    """
    parser = EFG_XMLParser()
    return parser.get_creation_ref(path)


def extract_item_type(self, path):
    """
    Extract the creation type from the incoming XML file.
    """
    parser = EFG_XMLParser()
    return parser.get_creation_type(path)


def lookup_content(self, path, source_id):
    '''
    Look for a filename in the form of:
    ARCHIVE_SOURCEID.[extension]
    '''
    content_path = None
    content_filename = None
    files = [f for f in os.listdir(path) if not f.endswith('.xml')]
    for f in files:
        tokens = os.path.splitext(f)[0].split('_')
        if len(tokens) == 0:
            continue
        if tokens[-1] == source_id:
            log.info('Content file FOUND: {0}'.format(f))
            content_path = os.path.join(path, f)
            content_filename = f
            break
    return content_path, content_filename


def extract_descriptive_metadata(self, path, item_type, item_node):
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
    parser = EFG_XMLParser()
    record = parser.get_creation_by_type(path, item_type)
    # log.debug(EFG_XMLParser.prettify(record))
    repo = CreationRepository(self.graph)
    av = (item_type == 'Video')
    creation = None
    if item_type == 'Video':
        # parse AV_Entity
        creation = parser.parse_av_creation(record)
    elif item_type == 'Image':
        # parse NON AV_Entity
        creation = parser.parse_non_av_creation(record)
    else:
        # should never be reached
        raise Exception(
            "Extracting metadata for type {} not yet implemented".format(item_type))
    log.debug(creation['properties'])
    if len(parser.warnings) > 0:
        # save warnings
        meta_source = item_node.meta_source.single()
        meta_source.warnings = parser.warnings
        meta_source.save()
    repo.create_entity(
        creation['properties'], item_node, creation['relationships'], av)


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
    Returns a random filename, chosen among the jpg files of the given path
    """
    jpg_files = [f for f in os.listdir(path) if f.endswith('.jpg')]
    index = random.randrange(0, len(jpg_files))
    return os.path.join(
        os.path.dirname(path), jpg_files[index])


def extract_tvs_vim_annotations(self, item, analyze_dir_path):
    """
    Extract temporal video segmentation and video quality results from
    storyboard.json file and save them as Annotation in the database.
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
    vim_estimations = []
    for s in data['shots']:
        shot = Shot()
        shot.shot_num = s['shot_num']
        shot.start_frame_idx = s['first_frame']
        shot.end_frame_idx = s['last_frame']
        shot.timestamp = s['timecode']
        try:
            shot.duration = s['len_seconds']
        except ValueError:
            log.warning("Invalid duration in the shot {0} \
                for value '{1}'".format(shot.shot_num, s['len_seconds']))
            shot.duration = None

        shot.thumbnail_uri = os.path.join(tvs_dir_path, s['img'])
        shots.append(shot)
        vim_estimations.append((shot.shot_num, s['motions_dict']))

    if len(shots) == 0:
        log.warning("Shots CANNOT be found in the file [%s]" % tvs_path)
        return

    # Save Shots in the database
    repo = AnnotationRepository(self.graph)
    repo.create_tvs_annotation(item, shots)
    repo.create_vim_annotation(item, vim_estimations)

    log.info('Extraction of TVS and VIM info completed')
