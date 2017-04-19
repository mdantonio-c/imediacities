# -*- coding: utf-8 -*-

"""
Handle your video metadata
"""

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
    Get a video if its id is passed as an argument.
    Else return all videos in the repository.
    """
    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, video_id=None):
        logger.debug("getting video id: %s", video_id)
        self.initGraph()
        data = []

        if video_id is not None:
            # check if the video exists
            try:
                v = self.graph.Video.nodes.get(uuid=video_id)
            except self.graph.Video.DoesNotExist:
                logger.debug("Video with uuid %s does not exist" % video_id)
                raise RestApiException(
                    "Please specify a valid video id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            videos = [v]
        else:
            videos = self.graph.Video.nodes.all()

        for v in videos:
            video = self.getJsonResponse(v)
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
    #             errors=[{"Bad Request": "Missing title"}],
    #             code=hcodes.HTTP_BAD_REQUEST
    #         )

    #     if 'description' not in data:
    #         return self.force_response(
    #             errors=[{"Bad Request": "Missing description"}],
    #             code=hcodes.HTTP_BAD_REQUEST
    #         )

    #     if 'duration' not in data:
    #         return self.force_response(
    #             errors=[{"Bad Request": "Missing duration"}],
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
    # @authentication.authorization_required
    # @decorate.apimethod
    def get(self, video_id):
        logger.info("get annotations for video id: %s", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()
        data = []

        try:
            self.graph.Video.nodes.get(uuid=video_id)
        except self.graph.Video.DoesNotExist:
            logger.debug("Video with uuid %s does not exist" % video_id)
            raise RestApiException(
                "Please specify a valid video id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        # video = self.graph.Video.nodes.get(uuid=video_id)
        # if video is None:
        #     raise RestApiException("Video not found")

        return self.force_response(data)
