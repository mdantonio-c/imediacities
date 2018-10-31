# -*- coding: utf-8 -*-

import os
import json
import random
import re
import traceback

from imc.tasks.services.efg_xmlparser import EFG_XMLParser
from imc.tasks.services.orf_xmlparser import ORF_XMLParser
from imc.tasks.services.creation_repository import CreationRepository
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.tasks.services.od_concept_mapping import concept_mapping
from imc.models import codelists
from operator import itemgetter


from utilities.logs import get_logger
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.flask_ext.flask_celery import CeleryExt
from restapi.services.mail import send_mail, get_html_template

celery_app = CeleryExt.celery_app

log = get_logger(__name__)

try:
    from scripts.analysis.analyze import (make_movie_analize_folder,
                                          analize,
                                          update_storyboard)
except BaseException:
    log.warning("Unable to import analyze script, not required in backend")


####################
# Define your celery tasks

def progress(self, state, info):
    if info is not None:
        log.info("%s [%s]" % (state, info))
    self.update_state(state=state)


@celery_app.task(bind=True)
def update_metadata(self, path, resource_id):
    with celery_app.app.app_context():

        log.debug("Starting task update_metadata for resource_id %s" %
                  resource_id)
        progress(self, 'Starting update metadata', path)
        self.graph = celery_app.get_service('neo4j')
        xml_resource = None
        try:
            metadata_update = True  # voglio proprio fare l'aggiornamento dei metadati!
            xml_resource, group, source_id, item_type, item_node = update_meta_stage(
                self, resource_id, path, metadata_update)
            log.debug(
                "Completed task update_metadata for resource_id %s" % resource_id)

            progress(self, 'Completed', path)

        except Exception as e:
            progress(self, 'Failed updating metadata', path)
            raise e

        return 1


@celery_app.task(bind=True)
def import_file(self, path, resource_id, mode, metadata_update=True):
    with celery_app.app.app_context():

        progress(self, 'Starting import', path)

        self.graph = celery_app.get_service('neo4j')

        xml_resource = None
        try:
            metadata_update = True  # voglio proprio fare l'aggiornamento dei metadati!
            xml_resource, group, source_id, item_type, item_node = update_meta_stage(
                self, resource_id, path, metadata_update)
            log.debug(
                "Completed task update_metadata for resource_id %s" % resource_id)
            progress(self, 'Updated metadata', path)
        except Exception as e:
            progress(self, 'Failed updating metadata', path)
            log.error("Task error, %s" % e)
            raise e

        try:
            # To ensure that the content item and its metadata will be
            # correctly linked in the system and its repositories,
            # FHI-Partners are expected to name the content item file,
            # using the following method:
            # The FHI project acronym_the FHI content ID (this is the
            # Content item ID in the local FHI’s database).
            # For example: CRB_1234.mp4
            filename, file_extension = os.path.splitext(path)
            if file_extension.startswith("."):
                file_extension = file_extension[1:]
            log.debug('filename [{0}], extension [{1}]'.format(
                filename, file_extension))
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
                    content_node = self.graph.ContentStage.nodes.get(
                        **properties)
                    log.debug("Content resource already exist for %s" %
                              content_path)
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
                    if content_node is not None:
                        content_node.status = 'SKIPPED'
                        content_node.status_message = 'Nothing to declare'
                        content_node.save()
                    return 1
                fast = (mode == 'fast')

            if content_node is None:
                raise Exception(
                    "Pipeline cannot be started: " +
                    "content does not exist in the path {0} for source ID {1}"
                    .format(basedir, source_id))

            content_node.status = "IMPORTING"
            content_node.save()

            # EXECUTE AUTOMATC TOOLS

            # Before starting I want to be sure that no automatic annotations
            # exist. It is dangerous re-processing in case of different fps.
            repo = AnnotationRepository(self.graph)
            if repo.check_automatic_tagging(item_node.uuid):
                log.warn(
                    "Pipeline cannot be started: " +
                    "delete automatic tags before re-processing!")
                content_node.status = "COMPLETED"
                content_node.save()
                return 1

            content_item = os.path.join('/uploads', content_path)
            if not os.path.exists(content_item):
                raise Exception('Bad input file', content_item)

            creation = item_node.creation.single()
            if not creation:
                raise ValueError('Unexpected missing creation '
                                 'importing resource {}'.format(resource_id))

            out_folder = make_movie_analize_folder(content_item,
                                                   (mode is not None and mode == 'clean'))
            if out_folder == "":
                raise Exception('Failed to create out_folder')

            log.info("Analize " + content_item)
            if analize(content_item, creation.uuid, item_type, out_folder, fast):
                log.info('Analize executed')
            else:
                raise Exception('Analize terminated with errors')

            analyze_path = '/uploads/Analize/' + \
                group.uuid + '/' + content_filename.split('.')[0] + '/'
            log.debug('analyze path: {0}'.format(analyze_path))

            # SAVE AUTOMATIC ANNOTATIONS

            progress(self, 'Extracting automatic annotations', path)

            # take the previous fps apart
            old_fps = item_node.framerate
            extract_tech_info(self, item_node, analyze_path)

            # - ONLY for videos -
            if item_type == 'Video':

                if old_fps != item_node.framerate:
                    log.info("Re-importing video item [{id}] with different fps: {old_fps} --> {new_fps}"
                             .format(id=item_node.uuid, old_fps=old_fps, new_fps=item_node.framerate))

                # extract TVS and VIM results
                shots, vim_estimations = extract_tvs_vim_results(
                    self, item_node, analyze_path)

                # first remove existing automatic VIM annotations if any
                vim_annotations = item_node.sourcing_annotations.search(
                    annotation_type='VIM', generator='FHG')
                for anno in vim_annotations:
                    anno_id = anno.id
                    repo.delete_vim_annotation(anno)
                    log.debug("Deleted existing VIM annotation [%s]" % anno_id)
                # save or update TVS annotations
                existing_shots = item_node.shots.all()
                if not existing_shots:
                    repo.create_automatic_tvs(item_node, shots)
                else:
                    # in order to preserve annotations we need to pass the list
                    # of annotations together with the new shot list and
                    # reposition accordingly them all in case of different a
                    # fps.
                    arrange_manual_annotations(self, item_node, shots, old_fps)
                    repo.update_automatic_tvs(
                        item_node, shots, vim_estimations)

                # save VIM annotations
                repo.create_vim_annotation(item_node, vim_estimations)

            # extract automatic object detection results
            try:
                extract_od_annotations(self, item_node, analyze_path)
            except IOError:
                log.warn('Could not find OD results file.')

            content_node.status = 'COMPLETED'
            content_node.status_message = 'Nothing to declare'
            content_node.save()

            progress(self, 'Completed', path)

        except Exception as e:
            # progress(self, 'Import error', None)
            progress(self, 'FAILED', None)
            log.error("Task error, %s" % e)
            if content_node is not None:
                content_node.status = 'ERROR'
                content_node.status_message = str(e)
                content_node.save()
            elif xml_resource is not None:
                xml_resource.warnings.append(str(e))
                xml_resource.save()
            # raise e

        return 1


def arrange_manual_annotations(self, item, new_shot_list, old_fps):
    '''
    Set the new shot list with the current annotations from the existing shot
    list. If the framerate is changed then those annotations have to be
    rearranged accordingly.

    Parameters
    ----------
    item : <node>
    new_shot_list : <dict>
    '''
    log.info("Set the new shot list with the current annotations for video [{}]"
             .format(item.uuid))
    for shot in item.shots.all():
        log.debug('-----------------------------------------------------')
        # key frame
        fk = (shot.end_frame_idx + shot.start_frame_idx) / 2
        log.debug('shot[{}] - key frame: {}'.format(shot.shot_num, fk))
        # target frame
        ft = round(fk * eval(item.framerate) / eval(old_fps))
        log.debug('target frame: {}'.format(ft))

        # get current manual annotations for this shot
        annotations = []
        for anno in shot.annotation.search(generator__isnull=True):
            log.debug(anno)
            annotations.append(anno.uuid)
        log.debug('shot[{}] - manual annotations:{}'
                  .format(shot.shot_num, annotations))

        # get target shot in the new shot list
        for shot_num, properties in new_shot_list.items():
            if properties['start_frame_idx'] <= ft <= properties['end_frame_idx']:
                log.info('Append annotation list {list} to the new shot '
                         '{shot_num} [{shot_start}-{shot_end}]'.format(
                             list=annotations,
                             shot_num=shot_num,
                             shot_start=properties['start_frame_idx'],
                             shot_end=properties['end_frame_idx']))
                if 'annotations' not in properties:
                    properties['annotations'] = []
                properties['annotations'].extend(annotations)
                break
        log.debug('-----------------------------------------------------')


@celery_app.task(bind=True)
def launch_tool(self, tool_name, item_id):
    with celery_app.app.app_context():
        log.debug('launch tool {0} for item {1}'.format(tool_name, item_id))
        if tool_name != 'object-detection':
            raise ValueError('Unexpected tool for: {}'.format(tool_name))

        self.graph = celery_app.get_service('neo4j')
        try:
            item = self.graph.Item.nodes.get(uuid=item_id)
            content_source = GraphBaseOperations.getSingleLinkedNode(
                item.content_source)
            group = GraphBaseOperations.getSingleLinkedNode(
                item.ownership)
            movie = content_source.filename
            analyze_path = '/uploads/Analize/' + \
                group.uuid + '/' + movie.split('.')[0] + '/'
            log.debug('analyze path: {0}'.format(analyze_path))
            # call analyze for object detection ONLY
            # if detect_objects(movie, analyze_path):
            #     log.info('Object detection executed')
            # else:
            #     raise Exception('Object detection terminated with errors')

            # here we expect object detection results in orf.xml
            extract_od_annotations(self, item, analyze_path)
        except Exception as e:
            log.error("Task error, %s" % e)
            raise e
        return 1


@celery_app.task(bind=True)
def shot_revision(self, revision, item_id):
    log.info('Start shot revision task for video item [{0}]'.format(item_id))
    self.graph = celery_app.get_service('neo4j')
    # get reviser
    reviser = self.graph.User.nodes.get_or_none(uuid=revision['reviser'])
    exitRevision = True if 'exitRevision' in revision and revision['exitRevision'] else False
    item = None
    try:
        item = self.graph.Item.nodes.get(uuid=item_id)
        content_source = GraphBaseOperations.getSingleLinkedNode(
            item.content_source)
        group = GraphBaseOperations.getSingleLinkedNode(
            item.ownership)
        movie = content_source.filename
        analyze_path = '/uploads/Analize/' + \
            group.uuid + '/' + movie.split('.')[0] + '/'
        log.debug('analyze path: {0}'.format(analyze_path))

        revised_cuts = []
        for s in sorted(revision['shots'], key=itemgetter('shot_num'))[1:]:
            revised_cuts.append(s['cut'])
        log.info('new list of cuts: {}'.format(revised_cuts))
        update_storyboard(revised_cuts, analyze_path)

        # extract new TVS and VIM results
        shots, vim_estimations = extract_tvs_vim_results(
            self, item, analyze_path)

        # extract 'confirmed' and 'double_check' flags
        for s in revision['shots']:
            shot_num = s['shot_num']
            # if shot_num == 0:
            #     continue
            shot = shots.get(shot_num)
            if shot is None:
                # should never be reached
                log.warn('Shot {} cannot be found'.format(shot_num))
                continue
            shot['revision_confirmed'] = s.get('confirmed', False)
            shot['revision_check'] = s.get('double_check', False)
            shot['annotations'] = s.get('annotations', [])

        repo = AnnotationRepository(self.graph)
        # first remove existing automatic VIM annotations if any
        vim_annotations = item.sourcing_annotations.search(
            annotation_type='VIM', generator='FHG')
        for anno in vim_annotations:
            anno_id = anno.id
            repo.delete_vim_annotation(anno)
            log.debug("Deleted existing VIM annotation [%s]" % anno_id)

        # update TVS annotations
        repo.update_automatic_tvs(item, shots, vim_estimations, True, reviser)

        # save VIM annotations
        repo.create_vim_annotation(item, vim_estimations)

    except Exception as e:
        log.error("Shot revision task has encountered some problems. %s" % e)
        aventity = GraphBaseOperations.getSingleLinkedNode(
            item.creation).downcast()
        replaces = {
            "title": aventity.identifying_title,
            "vid": aventity.uuid,
            "task_id": "",
            "failure": ""
        }
        # send an email to the reviser (and to the administrator)
        failure = traceback.format_exc()
        send_notification(self, reviser.email, 'Error in shot revision',
                          'shot_revision_failure.html', replaces,
                          self.request.id, failure)
    finally:
        if exitRevision:
            item.revision.disconnect_all()
        else:
            assignee = item.revision.single()
            rel = item.revision.relationship(assignee)
            rel.state = 'W'
            rel.save()

    log.info('Shot revision task completed successfully (exit: {exit})'.format(
        exit=exitRevision))
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
    # nel source_id i caratteri che non sono lettere
    # o numeri vanno sostituiti con trattino per la ricerca
    # del file del contenuto
    source_id_encoded = re.sub(r'[\W_]+', '-', source_id)
    log.debug('source_id_encoded: ' + source_id_encoded)

    content_path = None
    content_filename = None
    files = [f for f in os.listdir(path) if not f.endswith('.xml')]
    for f in files:
        tokens = os.path.splitext(f)[0].split('_')
        if len(tokens) == 0:
            continue
        if tokens[-1] == source_id_encoded:
            log.info('Content file FOUND: {0}'.format(f))
            content_path = os.path.join(path, f)
            content_filename = f
            break
    return content_path, content_filename


def update_meta_stage(self, resource_id, path, metadata_update):
    """
    Update data of MetaStage (that has resource_id) with data coming from xml
    file in path
    - If metadata_update=false and creation exists then nothing is updated
    - If Item and Creation don't exist then it creates them
    Return xml_resource (the updated MetaStage), group, source_id, item_type,
    item_node.
    """
    xml_resource = None
    try:
        xml_resource = self.graph.MetaStage.nodes.get(uuid=resource_id)

        if xml_resource is not None:

            group = GraphBaseOperations.getSingleLinkedNode(
                xml_resource.ownership)

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
            if item_node is None:
                item_properties = {}
                item_properties['item_type'] = item_type
                item_node = self.graph.Item(**item_properties).save()
                item_node.ownership.connect(group)
                item_node.meta_source.connect(xml_resource)
                item_node.save()
                log.debug("Item resource created for resource_id=%s" %
                          resource_id)

            # check for existing creation
            creation = item_node.creation.single()
            if creation is not None and not metadata_update:
                log.info("Skip updating metadata for resource_id=%s" %
                         resource_id)
            else:
                # update metadata
                log.debug("Updating metadata for resource_id=%s" % resource_id)
                xml_resource.warnings = extract_descriptive_metadata(
                    self, path, item_type, item_node)
                log.info("Metadata updated for resource_id=%s" % resource_id)

                xml_resource.status = 'COMPLETED'
                xml_resource.status_message = 'Nothing to declare'
                xml_resource.save()
        else:
            log.warning("Not found MetaStage for resource_id=%s" % resource_id)

    except Exception as e:
        log.error("Failed update of resource_id %s, Error: %s" %
                  (resource_id, e))
        if xml_resource is not None:
            xml_resource.status = 'ERROR'
            xml_resource.status_message = str(e)
            xml_resource.save()
        raise e
    return xml_resource, group, source_id, item_type, item_node


def extract_descriptive_metadata(self, path, item_type, item_node):
    """
    Simple metadata ingestion:
      - get record by type
      - validate against specification rules (D6.1)
      - extract expected data into dictionaries: props and relationships
      - save the model creating the entity into the database
      - return the list of possible warnings
    notes:
      - only EFG xml file allowed
      - warnings allowed for optional invalid elements
      - raise ValueError whenever those conditions are not met
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
            "Extracting metadata for type {} not yet implemented".format(
                item_type))
    # log.debug(creation['properties'])
    repo.create_entity(
        creation['properties'], item_node, creation['relationships'], av)
    return parser.warnings


def extract_tech_info(self, item, analyze_dir_path):
    """
    Extract technical information about the given content from result file
    origin_info.json and save them as Item properties in the database.
    """
    if not os.path.exists(analyze_dir_path):
        raise IOError(
            "Analyze results does not exist in the path %s", analyze_dir_path)

    # check for info result
    tech_info_filename = 'transcoded_info.json'
    tech_info_path = os.path.join(
        os.path.dirname(analyze_dir_path), tech_info_filename)
    if not os.path.exists(tech_info_path):
        log.warning("Technical info CANNOT be extracted: [%s] does not exist",
                    tech_info_path)
        return

    # load info from json
    with open(tech_info_path) as data_file:
        data = json.load(data_file)

    item.digital_format = [None for _ in range(4)]
    if item.item_type == 'Video':
        # get the thumbnail assigned to a given AV digital object
        thumbnails_uri = os.path.join(analyze_dir_path, 'thumbs/')
        item.thumbnail = get_thumbnail(thumbnails_uri)
        # duration
        item.duration = data["streams"][0]["duration"]
        # framerate
        item.framerate = data["streams"][0]["avg_frame_rate"]
        # dimension
        item.dimension = data["format"]["size"]
        # format
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

        # summary
        summary_filename = 'summary.jpg'
        summary_path = os.path.join(
            os.path.dirname(analyze_dir_path), summary_filename)
        if not os.path.exists(summary_path):
            log.warning("{0} CANNOT be found in the path: [{1}]".format(
                        summary_filename, analyze_dir_path))
        else:
            item.summary = summary_path

    elif item.item_type == 'Image':
        item.uri = data['image']['name']
        thumbnail_filename = 'transcoded_small.jpg'
        thumbnail_uri = os.path.join(
            os.path.dirname(analyze_dir_path), thumbnail_filename)
        item.thumbnail = (thumbnail_uri
                          if os.path.exists(thumbnail_uri)
                          else data['image']['name'])

        # filesize MUST be an Iteger of bytes (not e.g. 4.1KB)
        item.dimension = os.path.getsize(item.uri)

        # format
        # container: e.g."AVI", "MP4", "3GP", TIFF
        item.digital_format[0] = data['image']['format']
        # coding: e.g. "WMA","WMV", "MPEG-4", "RealVideo"
        item.digital_format[1] = data['image']["compression"]
        # format: RFC 2049 MIME types, e.g. "image/jpg", etc.
        item.digital_format[2] = data['image']['mimeType']
        # resolution: The degree of sharpness of the digital object expressed in
        # lines or pixel
        item.digital_format[3] = str(data['image']['geometry']['width']) \
            + 'x' + str(data['image']['geometry']['height'])

    else:
        log.warning('Invalid type. Technical info CANNOT be extracted for '
                    'Item[{uuid}] with type {type}'.format(
                        uuid=item.uuid, type=item.item_type))
        return

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


def extract_tvs_vim_results(self, item, analyze_dir_path):
    """
    Extract temporal video segmentation and video quality results from
    storyboard.json file.

    Returns:
    - shots: <dict(shot_num: {shot_properties})>
    - vim_estimations: (shot_num, {motions_dict})
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

    log.debug('Get shots and vimotion from file [%s]' % tvs_path)

    # load info from json
    with open(tvs_path) as data_file:
        data = json.load(data_file)

    shots = {}
    vim_estimations = []
    for s in data['shots']:
        try:
            duration = s['len_seconds']
        except ValueError:
            log.warning("Invalid duration in the shot {0} \
                for value '{1}'".format(s['shot_num'], s['len_seconds']))
            duration = None
        shots[s['shot_num']] = {
            'start_frame_idx': s['first_frame'],
            'end_frame_idx': s['last_frame'],
            'timestamp': s['timecode'],
            'duration': duration,
            'thumbnail_uri': os.path.join(tvs_dir_path, s['img'])
        }
        vim_estimations.append((s['shot_num'], s['motions_dict']))

    if len(shots) == 0:
        log.warning("Shots CANNOT be found in the file [%s]" % tvs_path)
        return

    log.info('Extraction of TVS and VIM info completed')
    return shots, vim_estimations


def extract_od_annotations(self, item, analyze_dir_path):
    '''
    Extract object detection results given by automatic analysis tool and
    ingest valueable annotations as 'automatic' TAGs.
    '''
    orf_results_filename = 'orf.xml'
    orf_results_path = os.path.join(
        os.path.dirname(analyze_dir_path), orf_results_filename)
    if not os.path.exists(orf_results_path):
        raise IOError(
            "Analyze results does not exist in the path %s", orf_results_path)
    log.info(
        'get automatic object detection from file [%s]' % orf_results_path)
    parser = ORF_XMLParser()
    frames = parser.parse(orf_results_path)

    # get the shot list of the item
    shots = item.shots.all()
    shot_list = {}
    for s in shots:
        shot_list[s.shot_num] = set()
    if item.item_type == 'Image':
        # consider a image like single frame shot
        shot_list[0] = set()
    object_ids = set()
    concepts = set()
    report = {}
    obj_cat_report = {}
    for timestamp, od_list in frames.items():
        '''
        A frame is a <dict> with timestamp<int> as key and a <list> as value.
        Each element in the list is a <tuple> that contains:
        (obj_id<str>, concept_label<str>, confidence<float>, region<list>).

        '''
        log.debug("timestamp: {0}, element: {1}".format(timestamp, od_list))
        for detected_object in od_list:
            concepts.add(detected_object[1])
            if detected_object[0] not in object_ids:
                report[detected_object[1]] = report.get(
                    detected_object[1], 0) + 1
            object_ids.add(detected_object[0])
            if item.item_type == 'Video':
                shot_uuid, shot_num = shot_lookup(self, shots, timestamp)
            elif item.item_type == 'Image':
                shot_num = 0
            if shot_num is not None:
                shot_list[shot_num].add(detected_object[1])
            # collect timestamp for keys:
            # (obj,cat) --> [(t1, confidence1, region1), (t2, confidence2, region2), ...]
            tmp = obj_cat_report.get(
                (detected_object[0], detected_object[1]), [])
            tmp.append((timestamp, detected_object[2], detected_object[3]))
            obj_cat_report[(detected_object[0], detected_object[1])] = tmp

    log.info('-----------------------------------------------------')
    log.info('Number of distinct detected objects: {}'.format(len(object_ids)))
    log.info('Number of distinct concepts: {}'.format(len(concepts)))
    log.info('Report of detected concepts per shot: {}'.format(shot_list))

    repo = AnnotationRepository(self.graph)
    counter = 0  # keep count of saved annotation
    for (key, timestamps) in obj_cat_report.items():
        if item.item_type == 'Video' and len(timestamps) < 5:
            # discard detections for short times
            continue
        # detect the concept
        concept_name = key[1]
        concept_iri = concept_mapping.get(concept_name)
        if concept_iri is None:
            log.warn('Cannot find concept <{0}> in the mapping'
                     .format(concept_name))
            # DO NOT create this annotation
            continue
        concept = {
            'iri': concept_iri,
            'name': concept_name
        }

        # detect target segment ONLY for videos
        start_frame = timestamps[0][0]
        end_frame = timestamps[-1][0]
        selector = {
            'type': 'FragmentSelector',
            'value': 't=' + str(start_frame) + ',' + str(end_frame)
        }

        # detection confidence
        confidence = []
        region_sequence = []
        for frame in list(range(start_frame, end_frame + 1)):
            found = False
            for value in timestamps:
                # value is a tuple like (timestamp<int>, confidence<float>, region<list>)
                if value[0] == frame:
                    confidence.append(value[1])
                    region_sequence.append(value[2])
                    found = True
                    break
            if not found:
                confidence.append(None)
                region_sequence.append(None)

        od_confidences = [e for e in confidence if e is not None]
        avg_confidence = sum(od_confidences) / float(len(od_confidences))
        if avg_confidence < 0.5:
            # discard detections with low confidence
            continue

        # save annotation
        bodies = []
        # warkaround for very huge area sequence!
        if len(region_sequence) > 1000:
            huge_size = len(region_sequence)
            region_sequence = []
            log.warn('Detected Object [{objID}/{concept}]: area sequence too big! Number of regions: {size}'.
                     format(objID=key[0], concept=concept['name'], size=huge_size))
        od_body = {
            'type': 'ODBody',
            'object_id': key[0],
            'confidence': avg_confidence,
            'region_sequence': region_sequence
        }
        od_body['concept'] = {'type': 'ResourceBody', 'source': concept}
        bodies.append(od_body)
        try:
            from neomodel import db as transaction
            transaction.begin()
            # log.debug("Automatic TAG. Body {0}, Selector {1}".format(
            #     bodies, selector))
            repo.create_tag_annotation(
                None, bodies, item, selector, False, None, True)
            transaction.commit()
        except Exception as e:
            log.verbose("Neomodel transaction ROLLBACK")
            try:
                transaction.rollback()
            except Exception as rollback_exp:
                log.warning(
                    "Exception raised during rollback: %s" % rollback_exp)
            raise e
        counter += 1
    log.info('Number of saved automatic annotations: {counter}'
             .format(counter=counter))
    log.info('-----------------------------------------------------')


def shot_lookup(self, shots, timestamp):
    for s in shots:
        if timestamp >= s.start_frame_idx and timestamp <= s.end_frame_idx:
            return s.uuid, s.shot_num


def send_notification(self, recipient, subject, template, replaces, task_id,
                      failure=None):
    """
    Send a notification email to a given recipient. If the failure is passed,
    an email is also sent to the system administrator with some more details
    about failure.
    """
    body = get_html_template(template, replaces)
    plain = "Sorry User, your job ID {task} is failed".format(task=task_id)
    send_mail(body, subject, recipient, plain_body=plain)

    if failure is not None:
        replaces['task_id'] = task_id
        replaces['failure'] = failure
        body = get_html_template(template, replaces)
        plain = "Job ID {task} is failed".format(task=task_id)
        send_mail(body, subject, plain_body=plain)
