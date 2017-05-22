# -*- coding: utf-8 -*-

"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

from rapydo.confs import get_api_url

from rapydo.utils.logs import get_logger
from rapydo import decorators as decorate
from rapydo.exceptions import RestApiException
from rapydo.utils import htmlcodes as hcodes
from rapydo.services.neo4j.graph_endpoints import GraphBaseOperations
from rapydo.services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.initGraph()
        data = []

        input_parameters = self.get_input()

        offset, limit = self.get_paging()
        # FIXME why get_paging doen't work with defaults
        offset = (1 if offset is None else offset)
        limit = (10 if limit is None else limit)
        logger.debug("page offset: {0}, page limit: {1}".format(
            offset, limit))

        term = input_parameters['term']
        if not term or not term.strip():
            raise RestApiException(
                'Term input cannot be empty',
                status_code=hcodes.HTTP_BAD_REQUEST)
        term = term.strip()
        if term == '*':
            # videos = self.graph.AVEntity.nodes.all()
            query = "MATCH (v:AVEntity) \
                      RETURN v SKIP {offset} LIMIT {limit}".format(
                offset=offset - 1,
                limit=limit)
        else:
            # videos = self.graph.AVEntity.nodes.filter(
            #     identifying_title__icontains=term)
            query = "MATCH (v:AVEntity) \
                      WHERE v.identifying_title =~ '(?i).*{term}.*' \
                      RETURN v SKIP {offset} LIMIT {limit}".format(
                term=term,
                offset=offset - 1,
                limit=limit)

        result = self.graph.cypher(query)
        videos = []
        for row in result:
            videos.append(self.graph.AVEntity.inflate(row[0]))

        api_url = get_api_url()
        for v in videos:
            video = self.getJsonResponse(v)
            logger.info("links %s " % video['links'])
            video['links']['self'] = api_url + \
                'api/videos/' + v.uuid
            video['links']['content'] = api_url + \
                'api/videos/' + v.uuid + '/content?type=video'
            video['links']['thumbnail'] = api_url + \
                'api/videos/' + v.uuid + '/content?type=thumbnail'
            data.append(video)

        return self.force_response(data)
