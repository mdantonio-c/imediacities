# -*- coding: utf-8 -*-

"""
Handle your video metadata
"""
import os
import re
from flask import stream_with_context, Response, request
from flask import send_file
from rapydo.confs import get_api_url

from rapydo.utils.logs import get_logger
from rapydo import decorators as decorate
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations
from rapydo.exceptions import RestApiException
from rapydo.services.neo4j.graph_endpoints import graph_transactions
from rapydo.services.neo4j.graph_endpoints import catch_graph_exceptions
from rapydo.utils import htmlcodes as hcodes

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
        self.initGraph()
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

        api_url = get_api_url()
        for v in videos:
            video = self.getJsonResponse(v)
            # video['links']['self'] = api_url + \
            #     'api/videos/' + v.uuid
            video['links']['content'] = api_url + \
                'api/videos/' + v.uuid + '/content?type=video'
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
        self.initGraph()

        v = self.get_input()
        if len(v) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)

        # schema = self.get_endpoint_custom_definition()

        data = self.get_input()

        logger.critical(data)

        return self.empty_response()

    # @decorate.catch_error()
    # @catch_graph_exceptions
    # @graph_transactions
    # def post(self, video_id=None):

    #     self.initGraph()

    #     try:
    #         data = request.get_json(force=True)
    #     except:
    #         data = {}

    #     logger.critical(data)

    #     if 'title' not in data:
    #         return self.force_response(
    #             errors=["Missing title"],
    #             code=hcodes.HTTP_BAD_REQUEST
    #         )

    #     if 'description' not in data:
    #         return self.force_response(
    #             errors=["Missing description"],
    #             code=hcodes.HTTP_BAD_REQUEST
    #         )

    #     if 'duration' not in data:
    #         return self.force_response(
    #             errors=["Missing duration"],
    #             code=hcodes.HTTP_BAD_REQUEST
    #         )

    #     video = self.graph.Video()
    #     video.id = getUUID()
    #     video.title = data["title"]
    #     video.description = data["description"]
    #     video.duration = data["duration"]
    #     video.save()

    #     return self.force_response(video.id)


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

        input_parameters = self.get_input()
        logger.debug("inputs %s" % input_parameters)

        self.initGraph()
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            logger.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        item = video.item.single()
        for a in item.targeting_annotations:
            annotation = self.getJsonResponse(a)
            data.append(annotation)

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

        self.initGraph()
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            logger.debug("AVEntity with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        item = video.item.single()
        api_url = get_api_url()
        vim_query = """
        MATCH (vim:Annotation {{annotation_type:'VIM'}})-[:HAS_TARGET]->(shot:Shot {{shot_num:{shot_num}}})
        MATCH (vim)-[:HAS_BODY]->(body:VIMBody)
        RETURN body
        """
        for s in item.shots.order_by('start_frame_idx'):
            shot = self.getJsonResponse(s)
            shot_url = api_url + 'api/shots/' + s.uuid
            shot['links']['self'] = shot_url
            shot['links']['thumbnail'] = shot_url + '?content=thumbnail'
            # get all shot annotations here
            shot['annotations'] = []
            # at the moment filter by vim annotation
            result = self.graph.cypher(vim_query.format(shot_num=s.shot_num))
            if result is not None and len(result) > 0:
                shot['annotations'].append(
                    self.getJsonResponse(
                        self.graph.VIMBody.inflate(result[0][0])))
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
                                    content_type != 'summary'):
            raise RestApiException(
                "Bad type parameter: expected 'video' or 'thumbnail'",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()
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

            return self.send_file_partial(video_uri, item.digital_format[2])

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

    def read_in_chunks(self, file_object, chunk_size=1024):
        """
        Lazy function (generator) to read a file piece by piece.
        Default chunk size: 1k.
        """
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def send_file_partial(self, path, mime):
        """
        Simple wrapper around send_file which handles HTTP 206 Partial Content
        (byte ranges)
        TODO: handle all send_file args, mirror send_file's error handling
        (if it has any)
        """
        range_header = request.headers.get('Range', None)
        if not range_header:

            logger.info("Providing streamed content of %s" % path)

            f = open(path, "rb")
            return Response(
                stream_with_context(self.read_in_chunks(f)),
                mimetype=mime)
            # return send_file(path)

        size = os.path.getsize(path)
        byte1, byte2 = 0, None

        m = re.search('(\d+)-(\d*)', range_header)
        g = m.groups()

        if g[0]:
            byte1 = int(g[0])
        if g[1]:
            byte2 = int(g[1])

        if byte2 is not None:
            length = byte2 + 1 - byte1
        else:
            length = size - byte1

        logger.info(
            "Providing partial content (bytes %s-%s, len = %s bytes) of %s"
            % (byte1, byte2, length, path)
        )

        data = None
        with open(path, 'rb') as f:
            f.seek(byte1)
            data = f.read(length)

        mime = "video/mp4"

        rv = Response(
            data, hcodes.HTTP_PARTIAL_CONTENT,
            mimetype=mime,
            direct_passthrough=True
        )
        rv.headers.add(
            'Content-Range', 'bytes %d-%d/%d'
            % (byte1, byte1 + length - 1, size)
        )
        rv.headers.add('Accept-Ranges', 'bytes')

        return rv
