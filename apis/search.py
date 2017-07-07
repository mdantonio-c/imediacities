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

        input_parameters = self.get_input()
        offset, limit = self.get_paging()
        block = 4

        #logger.debug("page offset: {0}, page limit: {1}".format(offset, limit))

        term = input_parameters.get('term', '').strip()
        if not term:
            raise RestApiException('Term input cannot be empty',
                                   status_code=hcodes.HTTP_BAD_REQUEST)

        logger.debug("first request to get the number of elements to be returned")

        if term == '*':
            countv = "MATCH (v:AVEntity) \
                    RETURN COUNT(DISTINCT(v))"
        else:
            countv = "MATCH (v:AVEntity) \
                    WHERE v.identifying_title =~ '(?i).*{term}.*' \
                    RETURN COUNT(DISTINCT(v))".format(term=term)

        #get total number of elements
        numels = self.graph.cypher(countv)

        logger.debug("Number of elements retrieved: {0}".format(numels[0][0]))

        numpage = int(input_parameters.get('numpage', ''))

        logger.debug("Page number: {0}".format(numpage))

        if (numpage < 0):
            raise RestApiException('Numpage input cannot be negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)

        pageblock = int(input_parameters.get('pageblock', ''))

        logger.debug("Block size: {0}".format(pageblock))

        if (pageblock < 0):
            raise RestApiException('Block size per page cannot be negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)

        block = pageblock
        offset = int(((numpage-1)*block))
        limit = int(offset+block)
        if (offset > numels[0][0]): 
                offset = 0
        if (limit > numels[0][0]): 
                limit = numels[0][0]

        logger.debug("page offset: {0}, page limit: {1}".format(offset, limit))

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
        api_url = get_api_url()
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

        #we got also the total number of elements retrieved
        data.append(numels)

        return self.force_response(data)
