# -*- coding: utf-8 -*-

"""
Handle your video entity
"""
import os
from flask import request, send_file
from utilities.helpers import get_api_url
from restapi.confs import PRODUCTION

from utilities.logs import get_logger
from imc.security import authz
from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.services.download import Downloader
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities import htmlcodes as hcodes
from imc.tasks.services.creation_repository import CreationRepository
from imc.tasks.services.annotation_repository import AnnotationRepository

from restapi.flask_ext.flask_celery import CeleryExt

log = get_logger(__name__)


#####################################
class Videos(GraphBaseOperations):

    """
    Get an AVEntity if its id is passed as an argument.
    Else return all AVEntities in the repository.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, video_id=None):
        log.debug("getting AVEntity id: %s", video_id)
        self.graph = self.get_service_instance('neo4j')
        data = []

        if video_id is not None:
            # check if the video exists
            try:
                v = self.graph.AVEntity.nodes.get(uuid=video_id)
            except self.graph.AVEntity.DoesNotExist:
                log.debug("AVEntity with uuid %s does not exist" % video_id)
                raise RestApiException(
                    "Please specify a valid video id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            videos = [v]
        else:
            videos = self.graph.AVEntity.nodes.all()

        api_url = get_api_url(request, PRODUCTION)
        for v in videos:
            video = self.getJsonResponse(
                v, max_relationship_depth=1,
                relationships_expansion=[
                    'record_sources.provider',
                    'item.ownership',
                    'item.revision',
                    'item.other_version'
                ]
            )
            item = v.item.single()
            # video['links']['self'] = api_url + \
            #     'api/videos/' + v.uuid
            video['links']['content'] = api_url + \
                'api/videos/' + v.uuid + '/content?type=video'
            if item.thumbnail is not None:
                video['links']['thumbnail'] = api_url + \
                    'api/videos/' + v.uuid + '/content?type=thumbnail'
            video['links']['summary'] = api_url + \
                'api/videos/' + v.uuid + '/content?type=summary'
            data.append(video)

        return self.force_response(data)

    """
    Create a new video description.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):
        self.graph = self.get_service_instance('neo4j')

        v = self.get_input()
        if len(v) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)

        # schema = self.get_endpoint_custom_definition()

        data = self.get_input()

        log.critical(data)

        return self.empty_response()

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, video_id):
        """
        Delete existing video description.
        """
        log.debug("deleting AVEntity id: %s", video_id)
        self.graph = self.get_service_instance('neo4j')

        if video_id is None:
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_REQUEST)
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
            repo = CreationRepository(self.graph)
            repo.delete_av_entity(v)
            return self.empty_response()
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)


class VideoAnnotations(GraphBaseOperations):
    """
        Get all video annotations for a given video.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, video_id):
        log.info("get annotations for AVEntity id: %s", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        params = self.get_input()
        anno_type = params.get('type')
        if anno_type is not None:
            anno_type = anno_type.upper()

        self.graph = self.get_service_instance('neo4j')
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()
        is_manual = params.get('onlyManual')
        if isinstance(is_manual, str) and (is_manual == '' or is_manual.lower() == 'true'):
            is_manual = True
        elif type(is_manual) == bool:
            # do nothing
            pass
        else:
            is_manual = False

        item = video.item.single()
        for a in item.targeting_annotations:
            if anno_type is not None and a.annotation_type != anno_type:
                continue
            creator = a.creator.single()
            if is_manual and (creator is None or creator.uuid != user.uuid):
                continue
            if a.private:
                if creator is None:
                    log.warn('Invalid state: missing creator for private '
                             'note [UUID:{}]'.format(a.uuid))
                    continue
                if creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(a, max_relationship_depth=0)
            del(res['links'])
            if a.annotation_type in ('TAG', 'DSC', 'TVS') and a.creator is not None:
                res['creator'] = self.getJsonResponse(
                    a.creator.single(), max_relationship_depth=0)
                del(res['creator']['links'])
            # attach bodies
            res['bodies'] = []
            for b in a.bodies.all():
                anno_body = b.downcast()
                body = self.getJsonResponse(
                    anno_body, max_relationship_depth=0)
                if 'links' in body:
                    del(body['links'])
                if a.annotation_type == 'TVS':
                    segments = []
                    for segment in anno_body.segments:
                        # look at the most derivative class
                        json_segment = self.getJsonResponse(
                            segment.downcast(), max_relationship_depth=0)
                        if 'links' in json_segment:
                            del(json_segment['links'])
                        # collect annotations and tags
                        # code duplicated for VideoShots.get
                        json_segment['annotations'] = []
                        json_segment['tags'] = []
                        # <dict(iri, name)>{iri, name, spatial, auto, hits}
                        tags = {}
                        for anno in segment.annotation.all():
                            if anno.private:
                                if creator is None:
                                    log.warn('Invalid state: missing creator for private '
                                             'note [UUID:{}]'.format(anno.uuid))
                                    continue
                                if creator is not None and creator.uuid != user.uuid:
                                    continue
                            s_anno = self.getJsonResponse(
                                anno, max_relationship_depth=0)
                            del(s_anno['links'])
                            if (anno.annotation_type in ('TAG', 'DSC') and
                                    creator is not None):
                                s_anno['creator'] = self.getJsonResponse(
                                    anno.creator.single(), max_relationship_depth=0)
                                del(s_anno['creator']['links'])
                            # attach bodies
                            s_anno['bodies'] = []
                            for b in anno.bodies.all():
                                mdb = b.downcast()  # most derivative body
                                s_anno['bodies'].append(
                                    self.getJsonResponse(mdb, max_relationship_depth=0))
                                if anno.annotation_type == 'TAG':
                                    spatial = None
                                    if 'ResourceBody' in mdb.labels():
                                        iri = mdb.iri
                                        name = mdb.name
                                        spatial = mdb.spatial
                                    elif 'TextualBody' in mdb.labels():
                                        iri = None
                                        name = mdb.value
                                    else:
                                        # unmanaged body type for tag
                                        continue
                                    ''' only for manual tag annotations  '''
                                    tag = tags.get((iri, name))
                                    if tag is None:
                                        tags[(iri, name)] = {
                                            'iri': iri,
                                            'name': name,
                                            'hits': 1
                                        }
                                        if spatial is not None:
                                            tags[(iri, name)
                                                 ]['spatial'] = spatial
                                    else:
                                        tag['hits'] += 1
                            json_segment['annotations'].append(s_anno)
                        json_segment['tags'] = list(tags.values())
                        segments.append(json_segment)
                    body['segments'] = segments
                res['bodies'] .append(body)
            data.append(res)

        return self.force_response(data)


class VideoShots(GraphBaseOperations):
    """
        Get the list of shots for a given video.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, video_id):
        log.info("get shots for AVEntity id: %s", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_user_if_logged()

        item = video.item.single()
        api_url = get_api_url(request, PRODUCTION)

        for s in item.shots.order_by('start_frame_idx'):
            shot = self.getJsonResponse(s)
            shot_url = api_url + 'api/shots/' + s.uuid
            shot['links']['self'] = shot_url
            shot['links']['thumbnail'] = shot_url + '?content=thumbnail'
            # get all shot annotations:
            # at the moment filter by vim and tag annotations
            shot['annotations'] = []
            for anno in s.annotation.all():
                creator = anno.creator.single()
                if anno.private:
                    if creator is None:
                        log.warn('Invalid state: missing creator for private '
                                 'note [UUID:{}]'.format(anno.uuid))
                        continue
                    if user is None or (creator is not None and creator.uuid != user.uuid):
                        continue
                res = self.getJsonResponse(anno, max_relationship_depth=0)
                del(res['links'])
                if (anno.annotation_type in ('TAG', 'DSC', 'LNK') and
                        creator is not None):
                    res['creator'] = self.getJsonResponse(
                        anno.creator.single(), max_relationship_depth=0)
                # attach bodies
                res['bodies'] = []
                for b in anno.bodies.all():
                    mdb = b.downcast()  # most derivative body
                    res['bodies'].append(
                        self.getJsonResponse(mdb, max_relationship_depth=0))
                shot['annotations'].append(res)

            # add automatic tags from "embedded segments"
            # for segment in s.embedded_segments.all():
            #     # get ONLY public tags
            #     for s_anno in segment.annotation.search(
            #             annotation_type='TAG', generator='FHG', private=False):
            #         res = self.getJsonResponse(s_anno, max_relationship_depth=0)
            #         del(res['links'])
            #         # attach bodies
            #         res['bodies'] = []
            #         for b in s_anno.bodies.all():
            #             mdb = b.downcast()  # most derivative body
            #             if 'ODBody' in mdb.labels():
            #                 # object detection body
            #                 concept = mdb.object_type.single()
            #                 res['bodies'].append(
            #                     self.getJsonResponse(concept, max_relationship_depth=0))
            #         shot['annotations'].append(res)
            query_auto_tags = "MATCH (s:Shot {{ uuid:'{shot_id}'}})-[:WITHIN_SHOT]-(sgm:VideoSegment) " \
                              "MATCH (sgm)<-[:HAS_TARGET]-(anno:Annotation {{annotation_type:'TAG', generator:'FHG'}})-[:HAS_BODY]-(b:ODBody)-[:CONCEPT]-(res:ResourceBody) " \
                              "RETURN anno, collect(res)".format(
                                  shot_id=s.uuid)
            result = self.graph.cypher(query_auto_tags)
            for row in result:
                auto_anno = self.graph.Annotation.inflate(row[0])
                res = self.getJsonResponse(auto_anno, max_relationship_depth=0)
                del(res['links'])
                # attach bodies
                res['bodies'] = []
                for concept in row[1]:
                    res['bodies'].append(
                        self.getJsonResponse(self.graph.ResourceBody.inflate(concept), max_relationship_depth=0))
                shot['annotations'].append(res)

            data.append(shot)

        return self.force_response(data)


class VideoSegments(GraphBaseOperations):
    """
        Get the list of manual segments for a given video.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, video_id, segment_id):
        if segment_id is not None:
            log.debug("get manual segment [uuid:{sid}] for AVEntity "
                      "[uuid:{vid}]".format(vid=video_id, sid=segment_id))
        else:
            log.debug("get all manual segments for AVEntity [uuid:{vid}]"
                      .format(vid=video_id))
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        # user = self.get_current_user()

        item = video.item.single()
        log.debug('get manual segments for Item [{}]'.format(item.uuid))
        # api_url = get_api_url(request, PRODUCTION)

        # TODO

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    def delete(self, video_id, segment_id):
        log.debug("delete manual segment [uuid:{sid}] for AVEntity "
                  "[uuid:{vid}]".format(vid=video_id, sid=segment_id))
        raise RestApiException(
            "Delete operation not yet implemented",
            status_code=hcodes.HTTP_NOT_IMPLEMENTED)

    @decorate.catch_error()
    @catch_graph_exceptions
    def put(self, video_id, segment_id):
        log.debug("update manual segment [uuid:{sid}] for AVEntity "
                  "[uuid:{vid}]".format(vid=video_id, sid=segment_id))
        raise RestApiException(
            "Update operation not yet implemented",
            status_code=hcodes.HTTP_NOT_IMPLEMENTED)


class VideoContent(GraphBaseOperations):

    __available_content_types__ = ('video', 'thumbnail', 'summary', 'orf')

    @decorate.catch_error()
    @catch_graph_exceptions
    @authz.pre_authorize
    def get(self, video_id):
        """
        Gets video content such as video strem and thumbnail
        """
        log.info("get video content for id %s" % video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()
        content_type = input_parameters['type']
        if content_type is None or content_type not in self.__available_content_types__:
            raise RestApiException(
                "Bad type parameter: expected one of %s." %
                (self.__available_content_types__, ),
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        item = video.item.single()
        if content_type == 'video':
            # TODO manage here content access (see issue 190)
            # always return the other version if available
            video_uri = item.uri
            other_version = item.other_version.single()
            if other_version is not None:
                video_uri = other_version.uri
            log.debug("video content uri: %s" % video_uri)
            if video_uri is None:
                raise RestApiException(
                    "Video not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            # all videos are converted to mp4
            mime = "video/mp4"
            download = Downloader()
            return download.send_file_partial(video_uri, mime)
        elif content_type == 'orf':
            # orf_uri = os.path.dirname(item.uri) + '/transcoded_orf.mp4'
            orf_uri = os.path.dirname(item.uri) + '/orf.mp4'
            if orf_uri is None or not os.path.exists(orf_uri):
                raise RestApiException(
                    "Video ORF not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            mime = "video/mp4"
            download = Downloader()
            return download.send_file_partial(orf_uri, mime)
        elif content_type == 'thumbnail':
            thumbnail_uri = item.thumbnail
            log.debug("thumbnail content uri: %s" % thumbnail_uri)
            thumbnail_size = input_parameters.get('size')
            # workaround when original thumnail is renamed by revision procedure
            if thumbnail_size is None and not os.path.exists(thumbnail_uri):
                log.debug('File {0} not found'.format(thumbnail_uri))
                thumbnail_filename = os.path.basename(thumbnail_uri)
                thumbs_dir = os.path.dirname(thumbnail_uri)
                f_name, f_ext = os.path.splitext(thumbnail_filename)
                tokens = f_name.split('_')
                if len(tokens) > 0:
                    f = 'f_' + tokens[-1] + f_ext
                    thumbnail_uri = os.path.join(thumbs_dir, f)
            if thumbnail_size is not None and thumbnail_size.lower() == 'large':
                # load image file in the parent folder with the same name
                thumbnail_filename = os.path.basename(thumbnail_uri)
                thumbs_parent_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(thumbnail_uri)))
                thumbnail_uri = os.path.join(
                    thumbs_parent_dir, thumbnail_filename)
                log.debug(
                    'request for large thumbnail: {}'.format(thumbnail_uri))
            if thumbnail_uri is None or not os.path.exists(thumbnail_uri):
                raise RestApiException(
                    "Thumbnail not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            return send_file(thumbnail_uri, mimetype='image/jpeg')
        elif content_type == 'summary':
            summary_uri = item.summary
            log.debug("summary content uri: %s" % summary_uri)
            if summary_uri is None:
                raise RestApiException(
                    "Summary not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            return send_file(summary_uri, mimetype='image/jpeg')
        else:
            # it should never be reached
            raise RestApiException(
                "Invalid content type: {0}".format(content_type),
                status_code=hcodes.HTTP_NOT_IMPLEMENTED)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def head(self, video_id):
        """
        Check for video content existance.
        """
        log.debug("check for video content existence with id %s" % video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()
        content_type = input_parameters['type']
        if content_type is None or content_type not in self.__available_content_types__:
            raise RestApiException(
                "Bad type parameter: expected one of %s." %
                (self.__available_content_types__, ),
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        item = video.item.single()
        headers = {}
        if content_type == 'video':
            if item.uri is None or not os.path.exists(item.uri):
                raise RestApiException(
                    "Video not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            headers['Content-Type'] = 'video/mp4'
        elif content_type == 'orf':
            orf_uri = os.path.dirname(item.uri) + '/orf.mp4'
            log.debug(orf_uri)
            if item.uri is None or not os.path.exists(orf_uri):
                raise RestApiException(
                    "Video ORF not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            headers['Content-Type'] = 'video/mp4'
        elif content_type == 'thumbnail':
            if item.thumbnail is None or not os.path.exists(item.thumbnail):
                raise RestApiException(
                    "Thumbnail not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            headers['Content-Type'] = 'image/jpeg'
        elif content_type == 'summary':
            if item.summary is None or not os.path.exists(item.summary):
                raise RestApiException(
                    "Summary not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            headers['Content-Type'] = 'image/jpeg'
        else:
            # it should never be reached
            raise RestApiException(
                "Invalid content type: {0}".format(content_type),
                status_code=hcodes.HTTP_NOT_IMPLEMENTED)
        return self.force_response([], headers=headers)


class VideoTools(GraphBaseOperations):

    __available_tools__ = ('object-detection', 'vimotion')

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self, video_id):

        log.debug('launch automatic tool for video id: %s' % video_id)

        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id.",
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        item = video.item.single()
        if item is None:
            raise RestApiException(
                "Item not available. Execute the pipeline first!",
                status_code=hcodes.HTTP_BAD_CONFLICT)
        if item.item_type != 'Video':
            raise RestApiException(
                "Content item is not a video. Use a valid video id.",
                status_code=hcodes.HTTP_BAD_REQUEST)

        params = self.get_input()
        if 'tool' not in params:
            raise RestApiException(
                'Please specify the tool to be launched.',
                status_code=hcodes.HTTP_BAD_REQUEST)
        tool = params['tool']
        if tool not in self.__available_tools__:
            raise RestApiException(
                "Please specify a valid tool. Expected one of %s." %
                (self.__available_tools__, ),
                status_code=hcodes.HTTP_BAD_REQUEST)

        repo = AnnotationRepository(self.graph)
        if ('operation' in params and params['operation'] == 'delete' and
                tool == self.__available_tools__[0]):
            # get all automatic tags
            for anno in item.sourcing_annotations:
                if anno.generator == 'FHG' and anno.annotation_type == 'TAG':
                    repo.delete_auto_annotation(anno)
            return self.empty_response()

        # DO NOT re-launch object detection twice for the same video!
        if repo.check_automatic_tagging(item.uuid):
            raise RestApiException(
                "Object detection CANNOT be run twice for the same video.",
                status_code=hcodes.HTTP_BAD_REQUEST)

        task = CeleryExt.launch_tool.apply_async(
            args=[tool, item.uuid],
            countdown=10
        )

        return self.force_response(task.id, code=hcodes.HTTP_OK_CREATED)


class VideoShotRevision(GraphBaseOperations):
    """Shot revision endpoint"""

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self):
        """Get all videos under revision"""
        log.debug('Getting videos under revision.')
        self.graph = self.get_service_instance('neo4j')
        data = []

        input_parameters = self.get_input()
        input_assignee = input_parameters['assignee']
        offset, limit = self.get_paging()
        offset -= 1
        log.debug("paging: offset {0}, limit {1}".format(offset, limit))
        if offset < 0:
            raise RestApiException('Page number cannot be a negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)
        if limit < 0:
            raise RestApiException('Page size cannot be a negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)

        # naive solution for getting VideoInRevision
        items = self.graph.Item.nodes.has(revision=True)
        for i in items:
            creation = i.creation.single()
            video = creation.downcast()
            assignee = i.revision.single()
            if input_assignee is not None and input_assignee != assignee.uuid:
                continue
            rel = i.revision.relationship(assignee)
            shots = i.shots.all()
            number_of_shots = len(shots)
            number_of_confirmed = len(
                [s for s in shots if s.revision_confirmed])
            # log.debug('number_of_shots {}'.format(number_of_shots))
            # log.debug('number_of_confirmed {}'.format(number_of_confirmed))
            percentage = 100 * number_of_confirmed / number_of_shots
            res = {
                'video': {
                    'uuid': video.uuid,
                    'title': video.identifying_title
                },
                'assignee': {
                    'uuid': assignee.uuid,
                    'name': assignee.name + ' ' + assignee.surname
                },
                'since': rel.when.isoformat(),
                'state': rel.state,
                'progress': percentage
            }
            data.append(res)

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def put(self, video_id):
        """Put a video under revision"""
        log.debug('Put video {0} under revision'.format(video_id))
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        item = v.item.single()
        if item is None:
            # 409: Video is not ready for revision. (should never be reached)
            raise RestApiException(
                "This AVEntity may not have been correctly imported. "
                "No ready for revision!",
                status_code=hcodes.HTTP_BAD_CONFLICT)

        user = self.get_current_user()
        iamadmin = self.auth.verify_admin()
        log.debug("Request for revision from user [{0}, {1} {2}]".format(
            user.uuid, user.name, user.surname))
        # Be sure user can revise this specific video
        assignee = user
        assignee_is_admin = iamadmin
        # allow admin to pass the assignee
        data = self.get_input()
        if iamadmin and 'assignee' in data:
            assignee = self.graph.User.nodes.get_or_none(uuid=data['assignee'])
            if assignee is None:
                # 400: description: Assignee not valid.
                raise RestApiException(
                    "Invalid candidate. User [{uuid}] does not exist".format(
                        uuid=data['assignee']),
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            # is the assignee an admin_root?
            assignee_is_admin = False
            for role in assignee.roles.all():
                if role.name == 'admin_root':
                    assignee_is_admin = True
                    break
        log.debug('Assignee is admin? {}'.format(assignee_is_admin))

        repo = CreationRepository(self.graph)

        if not assignee_is_admin and not repo.item_belongs_to_user(item, assignee):
            raise RestApiException(
                "User [{0}, {1} {2}] cannot revise video that does not belong to him/her".format(
                    user.uuid, user.name, user.surname),
                status_code=hcodes.HTTP_BAD_FORBIDDEN)
        if repo.is_video_under_revision(item):
            # 409: Video is already under revision.
            raise RestApiException(
                "Video [{uuid}] is already under revision".format(uuid=v.uuid),
                status_code=hcodes.HTTP_BAD_CONFLICT)

        repo.move_video_under_revision(item, assignee)
        # 204: Video under revision successfully.
        return self.empty_response()

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self, video_id):
        """Start a shot revision procedure"""
        log.debug('Start shot revision for video {0}'.format(video_id))
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)
        self.graph = self.get_service_instance('neo4j')
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        item = v.item.single()
        if item is None:
            # 409: Video is not ready for revision. (should never be reached)
            raise RestApiException(
                "This AVEntity may not have been correctly imported. "
                "No ready for revision!",
                status_code=hcodes.HTTP_BAD_CONFLICT)
        repo = CreationRepository(self.graph)
        # be sure video is under revision
        if not repo.is_video_under_revision(item):
            raise RestApiException(
                "This video [{vid}] is not under revision!".format(
                    vid=video_id),
                status_code=hcodes.HTTP_BAD_CONFLICT)
        # ONLY the reviser and the administrator can provide a new list of cuts
        user = self.get_current_user()
        iamadmin = self.auth.verify_admin()
        if not iamadmin and not repo.is_revision_assigned_to_user(item, user):
            raise RestApiException(
                "User [{0}, {1} {2}] cannot revise video that is not assigned to him/her".format(
                    user.uuid, user.name, user.surname),
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        revision = self.get_input()
        # validate request body
        if 'shots' not in revision or not revision['shots']:
            raise RestApiException(
                'Provide a valid list of cuts',
                status_code=hcodes.HTTP_BAD_REQUEST)
        for idx, s in enumerate(revision['shots']):
            if 'shot_num' not in s:
                raise RestApiException(
                    'Missing shot_num in shot: {}'.format(s),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if idx > 0 and 'cut' not in s:
                raise RestApiException(
                    'Missing cut for shot[{0}]'.format(s['shot_num']),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if 'confirmed' in s and not isinstance(s['confirmed'], bool):
                raise RestApiException(
                    'Invalid confirmed value',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if 'double_check' in s and not isinstance(s['double_check'], bool):
                raise RestApiException(
                    'Invalid double_check value',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if 'annotations' not in s:
                raise RestApiException(
                    'Missing annotations in shot: {}'.format(s),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if (
                'annotations' in s and
                not isinstance(s['annotations'], type(list)) and
                not all(isinstance(val, str) for val in s['annotations'])
            ):
                raise RestApiException(
                    'Invalid annotations value. Expected list<str>',
                    status_code=hcodes.HTTP_BAD_REQUEST)
        if 'exitRevision' in revision and not isinstance(revision['exitRevision'], bool):
            raise RestApiException(
                'Invalid exitRevision',
                status_code=hcodes.HTTP_BAD_REQUEST)

        revision['reviser'] = user.uuid
        # launch asynch task
        try:
            task = CeleryExt.shot_revision.apply_async(
                args=[revision, item.uuid],
                countdown=10,
                priority=5
            )
            assignee = item.revision.single()
            rel = item.revision.relationship(assignee)
            rel.state = 'R'
            rel.save()
            # 202: OK_ACCEPTED
            return self.force_response(task.id, code=hcodes.HTTP_OK_ACCEPTED)
        except BaseException as e:
            raise e

    @decorate.catch_error()
    @catch_graph_exceptions
    def delete(self, video_id):
        """Take off revision from a video"""
        log.debug('Exit revision for video {0}'.format(video_id))
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)
        self.graph = self.get_service_instance('neo4j')
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        item = v.item.single()
        if item is None:
            # 409: Video is not ready for revision. (should never be reached)
            raise RestApiException(
                "This AVEntity may not have been correctly imported. "
                "No ready for revision!",
                status_code=hcodes.HTTP_BAD_CONFLICT)

        repo = CreationRepository(self.graph)
        if not repo.is_video_under_revision(item):
            # 409: Video is already under revision.
            raise RestApiException(
                "Video [{uuid}] is not under revision".format(uuid=v.uuid),
                status_code=hcodes.HTTP_BAD_REQUEST)
        # ONLY the reviser and the administrator can exit revision
        user = self.get_current_user()
        iamadmin = self.auth.verify_admin()
        if not iamadmin and not repo.is_revision_assigned_to_user(item, user):
            raise RestApiException(
                "User [{0}, {1} {2}] cannot exit revision for video that is "
                "not assigned to him/her".format(
                    user.uuid, user.name, user.surname),
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        repo.exit_video_under_revision(item)
        # 204: Video revision successfully exited.
        return self.empty_response()
