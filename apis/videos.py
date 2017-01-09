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
