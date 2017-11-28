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

    allowed_item_types = ('all', 'video', 'image')
    allowed_term_fields = ('title', 'description', 'keyword', 'contributor')

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.initGraph()

        input_parameters = self.get_input()
        offset, limit = self.get_paging()
        offset -= 1
        logger.debug("paging: offset {0}, limit {1}".format(offset, limit))
        if offset < 0:
            raise RestApiException('Page number cannot be a negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)
        if limit < 0:
            raise RestApiException('Page size cannot be a negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)

        # check request for term matching
        match = input_parameters.get('match')
        if match is not None:
            term = match.get('term', '').strip()
            if not term:
                raise RestApiException('Term input cannot be empty',
                                       status_code=hcodes.HTTP_BAD_REQUEST)
            fields = match.get('fields')
            if fields is None or len(fields) == 0:
                raise RestApiException('Fields input cannot be empty',
                                       status_code=hcodes.HTTP_BAD_REQUEST)

        # check request for filtering
        filtering = input_parameters.get('filter')
        if filtering is not None:
            # check item type
            item_type = filtering.get('type', 'all').strip().lower()
            if item_type not in self.__class__.allowed_item_types:
                raise RestApiException(
                    "Bad item type parameter: expected one of %s" %
                    (self.__class__.allowed_item_types, ),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if item_type == 'all':
                entity = 'Creation'
            elif item_type == 'video':
                entity = 'AVEntity'
            elif item_type == 'image':
                entity = 'NonAVEntity'
            else:
                # should never be reached
                raise RestApiException(
                    'Unexpected item type',
                    status_code=hcodes.HTTP_SERVER_ERROR)

            provider = filtering.get('provider', '').strip()

        filters = ''
        if provider:
            filters = "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider) \
            WHERE p.identifier='{provider}'".format(provider=provider)

        # first request to get the number of elements to be returned
        if term == '*':
            countv = "MATCH (n:{entity}) \
                    {filters} \
                    RETURN COUNT(DISTINCT(n))".format(
                entity=entity,
                filters=filters)
        else:
            countv = "MATCH (n:{entity}) \
                    {filters} \
                    MATCH (n)-[r:HAS_TITLE]->(t:Title) WHERE t.text =~ '(?i).*{term}.*' \
                    RETURN COUNT(DISTINCT(n))".format(
                entity=entity,
                filters=filters,
                term=term)

        # get total number of elements
        numels = [row[0] for row in self.graph.cypher(countv)][0]
        logger.debug("Number of elements retrieved: {0}".format(numels))

        if term == '*':
            query = "MATCH (n:{entity}) \
                     {filters} \
                     RETURN n SKIP {offset} LIMIT {limit}".format(
                entity=entity,
                filters=filters,
                offset=offset,
                limit=limit)
        else:
            query = "MATCH (n:{entity}) \
                     {filters} \
                     MATCH (n)-[r:HAS_TITLE]->(t:Title) WHERE t.text =~ '(?i).*{term}.*' \
                     RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
                entity=entity,
                filters=filters,
                term=term,
                offset=offset,
                limit=limit)

        data = []
        result = self.graph.cypher(query)
        api_url = get_api_url(request, PRODUCTION)
        for row in result:
            if 'AVEntity' in row[0].labels:
                v = self.graph.AVEntity.inflate(row[0])
            elif 'NonAVEntity' in row[0].labels:
                v = self.graph.NonAVEntity.inflate(row[0])
            else:
                # should never be reached
                raise RestApiException(
                    'Unexpected item type',
                    status_code=hcodes.HTTP_SERVER_ERROR)

            item = v.item.single()
            video_url = api_url + 'api/videos/' + v.uuid
            # use depth 2 to get provider info from record source
            # TO BE FIXED
            video = self.getJsonResponse(v, max_relationship_depth=2)
            logger.info("links %s" % video['links'])
            video['links']['self'] = video_url
            video['links']['content'] = video_url + '/content?type=video'
            if item.thumbnail is not None:
                video['links']['thumbnail'] = video_url + '/content?type=thumbnail'
            video['links']['summary'] = video_url + '/content?type=summary'

            data.append(video)

        # return also the total number of elements
        return self.force_response(data, meta={"totalItems": numels})
