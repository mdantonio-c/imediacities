# -*- coding: utf-8 -*-

"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

from flask import request
from utilities.helpers import get_api_url
from restapi.confs import PRODUCTION

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
        logger.debug("paging: offset {0}, limit {1}".format(offset, limit))
        # block = 4

        # numpage = int(input_parameters.get('numpage', ''))
        # logger.debug("Page number: {0}".format(numpage))
        # if numpage < 0:
        #     raise RestApiException('Page number cannot be a negative value',
        #                            status_code=hcodes.HTTP_BAD_REQUEST)

        # pageblock = int(input_parameters.get('pageblock', ''))
        # logger.debug("Block size: {0}".format(pageblock))
        # if pageblock < 0:
        #     raise RestApiException('Page size cannot be a negative value',
        #                            status_code=hcodes.HTTP_BAD_REQUEST)

        term = input_parameters.get('term', '').strip()
        if not term:
            raise RestApiException('Term input cannot be empty',
                                   status_code=hcodes.HTTP_BAD_REQUEST)

        # first request to get the number of elements to be returned
        if term == '*':
            countv = "MATCH (v:AVEntity) \
                    RETURN COUNT(DISTINCT(v))"
        else:
            countv = "MATCH (v:AVEntity) \
                    WHERE v.identifying_title =~ '(?i).*{term}.*' \
                    RETURN COUNT(DISTINCT(v))".format(term=term)

        # get total number of elements
        numels = [row[0] for row in self.graph.cypher(countv)][0]
        logger.debug("Number of elements retrieved: {0}".format(numels))

        # block = pageblock
        # offset = int(((numpage - 1) * block))
        # limit = int(offset + block)
        # if (offset > numels):
        #         offset = 0
        # if (limit > numels):
        #         limit = numels

        # logger.debug("page offset: {0}, page limit: {1}".format(offset, limit))

        if term == '*':
            # videos = self.graph.AVEntity.nodes.all()
            query = "MATCH (v:AVEntity) \
                      RETURN v SKIP {offset} LIMIT {limit}".format(
                offset=offset,
                limit=limit)
        else:
            # videos = self.graph.AVEntity.nodes.filter(
            #     identifying_title__icontains=term)
            query = "MATCH (v:AVEntity) \
                      WHERE v.identifying_title =~ '(?i).*{term}.*' \
                      RETURN v SKIP {offset} LIMIT {limit}".format(
                term=term,
                offset=offset,
                limit=limit)

        data = []
        result = self.graph.cypher(query)
        api_url = get_api_url(request, PRODUCTION)
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

        # wreturn also the total number of elements
        data.append(numels)

        return self.force_response(data)
