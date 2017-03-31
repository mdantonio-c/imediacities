# -*- coding: utf-8 -*-

"""
Handle your video metadata
"""

from commons.logs import get_logger
from .. import decorators as decorate
from ..services.neo4j.graph_endpoints import GraphBaseOperations
from ..services.neo4j.graph_endpoints import myGraphError
from ..services.neo4j.graph_endpoints import returnError
from ..services.neo4j.graph_endpoints import graph_transactions
from ..services.neo4j.graph_endpoints import catch_graph_exceptions
from commons import htmlcodes as hcodes
# from commons.services.uuid import getUUID

logger = get_logger(__name__)


#####################################
class Videos(GraphBaseOperations):
    """
    Get a video if its id is passed as an argument. Else return all videos in the repository.
    """
    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
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
                return returnError(
                    self,
                    label="Invalid request",
                    error="Please specify a valid video id",
                    code=hcodes.HTTP_BAD_NOTFOUND)  
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
    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    @authentication.authorization_required
    # @decorate.apimethod
    def post(self):
        self.initGraph()

        v = self.get_input()
        if len(v) == 0:
            raise myGraphError(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)

        schema = self.get_endpoint_custom_definition()

        try:
            data = request.get_json(force=True)
        except:
            data = {}

        logger.critical(data)

        return self.empty_response()

    # @decorate.catch_error(
    #     exception=Exception, exception_label=None, catch_generic=False)
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
    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    # @authentication.authorization_required
    # @decorate.apimethod
    def get(self, video_id):
        logger.info("get annotations for video id: %s", video_id)
        if video_id is None:
            return returnError(
                self,
                label="Invalid request",
                error="Please specify a video id",
                code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()
        data = []

        try:
            v = self.graph.Video.nodes.get(uuid=video_id)
        except self.graph.Video.DoesNotExist:
            logger.debug("Video with uuid %s does not exist" % video_id)
            return returnError(
                self,
                label="Invalid request",
                error="Please specify a valid video id",
                code=hcodes.HTTP_BAD_NOTFOUND)  

        # video = self.graph.Video.nodes.get(uuid=video_id)
        # if video is None:
        #     raise myGraphError("Video not found")

        # TODO 

        return self.force_response(data)
