# -*- coding: utf-8 -*-

"""
Handle your videos
"""

from commons.logs import get_logger
from .. import decorators as decorate
from ...auth import authentication
# from flask_restful import request
from ..services.neo4j.graph_endpoints import GraphBaseOperations
# from ..services.neo4j.graph_endpoints import myGraphError
# from ..services.neo4j.graph_endpoints import returnError
from ..services.neo4j.graph_endpoints import graph_transactions
from ..services.neo4j.graph_endpoints import catch_graph_exceptions
# from commons import htmlcodes as hcodes
# from commons.services.uuid import getUUID

logger = get_logger(__name__)


#####################################
class Videos(GraphBaseOperations):

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @authentication.authorization_required
    # @decorate.apimethod
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
    # @authentication.authorization_required
    # # @decorate.apimethod
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

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @authentication.authorization_required
    # @decorate.apimethod
    def get_annotations(self, video_id=None):

        if user_id is None:

            return returnError(
                self,
                label="Invalid request",
                error="Please specify a video id",
                code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()
        data = []

        video = self.getNode(self.graph.Video, video_id, field='uuid')
        if video is None:
            raise myGraphError("Video not found")

        # if video_id is not None:
        #     v = self.graph.Video.nodes.get(id=video_id)
        #     videos = [v]
        # else:
        #     videos = self.graph.Video.nodes.all()

        # for v in videos:
        #     video = self.getJsonResponse(v)
        #     data.append(video)

        return self.force_response(data)
        



# class VideoAnnotation(GraphBaseOperations):
#     @decorate.catch_error(
#         exception=Exception, exception_label=None, catch_generic=False)
#     @catch_graph_exceptions
#     # @authentication.authorization_required
#     # @decorate.apimethod
#     def get(self, query=None):

#         self.initGraph()

#         data = []
#         cypher = "MATCH (g:Group)"

#         if query is not None:
#             cypher += " WHERE g.shortname =~ '(?i).*%s.*'" % query

#         cypher += " RETURN g ORDER BY g.shortname ASC"

#         if query is None:
#             cypher += " LIMIT 20"

#         result = self.graph.cypher(cypher)
#         for row in result:
#             g = self.graph.Group.inflate(row[0])
#             data.append({"id": g.uuid, "shortname": g.shortname})

#         return self.force_response(data)
