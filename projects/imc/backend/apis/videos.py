# -*- coding: utf-8 -*-

"""
Handle your video metadata
"""
import os
from flask import request, send_file
from utilities.helpers import get_api_url
from restapi.confs import PRODUCTION

from utilities.logs import get_logger
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

logger = get_logger(__name__)


#####################################
class Videos(GraphBaseOperations):

    """
    Get an AVEntity if its id is passed as an argument.
    Else return all AVEntities in the repository.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, video_id=None):
        logger.debug("getting AVEntity id: %s", video_id)
        self.graph = self.get_service_instance('neo4j')
        data = []

        if video_id is not None:
            # check if the video exists
            try:
                v = self.graph.AVEntity.nodes.get(uuid=video_id)
            except self.graph.AVEntity.DoesNotExist:
                logger.debug("AVEntity with uuid %s does not exist" % video_id)
                raise RestApiException(
                    "Please specify a valid video id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            videos = [v]
        else:
            videos = self.graph.AVEntity.nodes.all()

        api_url = get_api_url(request, PRODUCTION)
        for v in videos:
            # use depth 2 to get provider info from record source
            # TO BE FIXED
            video = self.getJsonResponse(v, max_relationship_depth=2)
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

        logger.critical(data)

        return self.empty_response()

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, video_id):
        """
        Delete existing video description.
        """
        logger.debug("deliting AVEntity id: %s", video_id)
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
            logger.debug("AVEntity with uuid %s does not exist" % video_id)
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
        logger.info("get annotations for AVEntity id: %s", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        params = self.get_input()
        logger.debug("inputs %s" % params)
        anno_type = params.get('type')
        if anno_type is not None:
            anno_type = anno_type.upper()

        self.graph = self.get_service_instance('neo4j')
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            logger.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()

        item = video.item.single()
        for a in item.targeting_annotations:
            if anno_type is not None and a.annotation_type != anno_type:
                continue
            if a.private:
                if a.creator is None:
                    logger.warn('Invalid state: missing creator for private '
                                'note [UUID:{}]'.format(a.uuid))
                    continue
                creator = a.creator.single()
                if creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(a, max_relationship_depth=0)
            del(res['links'])
            if a.annotation_type in ('TAG', 'DSC') and a.creator is not None:
                res['creator'] = self.getJsonResponse(
                    a.creator.single(), max_relationship_depth=0)
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
                        json_segment = self.getJsonResponse(
                            segment, max_relationship_depth=0)
                        if 'links' in json_segment:
                            del(json_segment['links'])
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
        logger.info("get shots for AVEntity id: %s", video_id)
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
            logger.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()

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
            shot['tags'] = []
            # <dict(iri, name)>{iri, name, spatial, auto, hits}
            tags = {}
            for anno in s.annotation.all():
                creator = anno.creator.single()
                if anno.private:
                    if creator is None:
                        logger.warn('Invalid state: missing creator for private '
                                    'note [UUID:{}]'.format(anno.uuid))
                        continue
                    if creator is not None and creator.uuid != user.uuid:
                        continue
                res = self.getJsonResponse(anno, max_relationship_depth=0)
                del(res['links'])
                if (anno.annotation_type in ('TAG', 'DSC') and
                        creator is not None):
                    res['creator'] = self.getJsonResponse(
                        anno.creator.single(), max_relationship_depth=0)
                # attach bodies
                res['bodies'] = []
                for b in anno.bodies.all():
                    mdb = b.downcast()  # most derivative body
                    res['bodies'] .append(
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
                                tags[(iri, name)]['spatial'] = spatial
                        else:
                            tag['hits'] += 1
                shot['annotations'].append(res)

            # add any other tags from "embedded segments"
            for segment in s.embedded_segments.all():
                # get ONLY public tags
                for s_anno in segment.annotation.search(annotation_type='TAG', private=False):
                    for b in s_anno.bodies.all():
                        mdb = b.downcast()  # most derivative body
                        if 'ODBody' in mdb.labels():
                            # object detection body
                            concept = mdb.object_type.single()
                            tag = tags.get((concept.iri, concept.name))
                            if tag is None:
                                tags[(concept.iri, concept.name)] = {
                                    'iri': concept.iri,
                                    'name': concept.name,
                                    'hits': 1
                                }
                            else:
                                tag['hits'] += 1
            shot['tags'] = list(tags.values())
            data.append(shot)

        return self.force_response(data)


class VideoContent(GraphBaseOperations):
    """
    Gets video content such as video strem and thumbnail
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, video_id):
        logger.info("get video content for id %s" % video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        input_parameters = self.get_input()
        content_type = input_parameters['type']
        if content_type is None or (content_type != 'video' and
                                    content_type != 'thumbnail' and
                                    content_type != 'summary' and
                                    content_type != 'orf'):
            raise RestApiException(
                "Bad type parameter: expected 'video' or 'thumbnail'",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            logger.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        item = video.item.single()
        if content_type == 'video':
            video_uri = item.uri
            logger.debug("video content uri: %s" % video_uri)
            if video_uri is None:
                raise RestApiException(
                    "Video not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)

            # mime = item.digital_format[2]
            # TO FIX: stored mime is MOV, non MP4, overwriting
            mime = "video/mp4"
            download = Downloader()
            return download.send_file_partial(video_uri, mime)
        elif content_type == 'orf':
            orf_uri = os.path.dirname(item.uri) + '/transcoded_orf.mp4'
            if orf_uri is None or not os.path.exists(orf_uri):
                raise RestApiException(
                    "Video ORF not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            mime = "video/mp4"
            download = Downloader()
            return download.send_file_partial(orf_uri, mime)
        elif content_type == 'thumbnail':
            thumbnail_uri = item.thumbnail
            logger.debug("thumbnail content uri: %s" % thumbnail_uri)
            if thumbnail_uri is None:
                raise RestApiException(
                    "Thumbnail not found",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            return send_file(thumbnail_uri, mimetype='image/jpeg')
        elif content_type == 'summary':
            summary_uri = item.summary
            logger.debug("summary content uri: %s" % summary_uri)
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


class VideoTools(GraphBaseOperations):

    __available_tools__ = ('object-detection', 'vimotion')

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self, video_id):

        logger.debug('launch automatic tool for video id: %s' % video_id)

        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            logger.debug("AVEntity with uuid %s does not exist" % video_id)
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

        # DO NOT re-launch object detection twice for the same video!
        repo = AnnotationRepository(self.graph)
        if repo.check_automatic_tagging(item.uuid):
            raise RestApiException(
                "Object detection CANNOT be run twice for the same video.",
                status_code=hcodes.HTTP_BAD_REQUEST)

        task = CeleryExt.launch_tool.apply_async(
            args=[tool, item.uuid],
            countdown=10
        )

        return self.force_response(task.id, code=hcodes.HTTP_OK_CREATED)
