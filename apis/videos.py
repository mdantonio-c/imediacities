# -*- coding: utf-8 -*-

"""
Handle your videos
"""

from commons.logs import get_logger
from .. import decorators as decorate
from ..services.neo4j.graph_endpoints import GraphBaseOperations
from ..services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Videos(GraphBaseOperations):

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    def get(self, video_id=None):

        self.initGraph()
        data = []

        if video_id is not None:
            v = self.graph.Video.nodes.get(id=video_id)
            videos = [v]
        else:
            videos = self.graph.Video.nodes.all()

        for v in videos:
            video = self.getJsonResponse(v)
            data.append(video)

        return self.force_response(data)

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
