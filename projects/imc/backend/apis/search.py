# -*- coding: utf-8 -*-

"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

from flask import request
from utilities.helpers import get_api_url

from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions

logger = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.initGraph()

        input_parameters = self.get_input()
        offset, limit = self.get_paging()

        logger.debug("page offset: {0}, page limit: {1}".format(offset, limit))

        term = input_parameters.get('term', '').strip()
        if not term:
            raise RestApiException('Term input cannot be empty',
                                   status_code=hcodes.HTTP_BAD_REQUEST)
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

        data = []
        result = self.graph.cypher(query)
        api_url = get_api_url(request)
        for row in result:
            v = self.graph.AVEntity.inflate(row[0])

            video_url = api_url + 'api/videos/' + v.uuid

            video = self.getJsonResponse(v)
            logger.info("links %s" % video['links'])
            video['links']['self'] = video_url
            video['links']['content'] = video_url + '/content?type=video'
            video['links']['thumbnail'] = video_url + '/content?type=thumbnail'
            video['links']['summary'] = video_url + '/content?type=summary'
            data.append(video)

        return self.force_response(data)
