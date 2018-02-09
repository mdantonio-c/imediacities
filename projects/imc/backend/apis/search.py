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
from imc.models import codelists

logger = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    allowed_item_types = ('all', 'video', 'image')  # , 'text')
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
        provider = None
        multi_match_query = ''
        multi_match = []
        multi_match_where = []
        match = input_parameters.get('match')
        if match is not None:
            term = match.get('term', '').strip()
            if not term:
                raise RestApiException('Term input cannot be empty',
                                       status_code=hcodes.HTTP_BAD_REQUEST)
            # clean up term from '*'
            term = term.replace("*", "")

            fields = match.get('fields')
            if fields is None or len(fields) == 0:
                raise RestApiException('Match term fields cannot be empty',
                                       status_code=hcodes.HTTP_BAD_REQUEST)
            for f in fields:
                if f not in self.__class__.allowed_term_fields:
                    raise RestApiException(
                        "Bad field: expected one of %s" %
                        (self.__class__.allowed_term_fields, ),
                        status_code=hcodes.HTTP_BAD_REQUEST)
                if not term:
                    # catch '*'
                    break
                if f == 'title':
                    multi_match.append("(n)-[:HAS_TITLE]->(t:Title)")
                    multi_match_where.append(
                        "t.text =~ '(?i).*{term}.*'".format(term=term))
                elif f == 'description':
                    multi_match.append(
                        "(n)-[:HAS_DESCRIPTION]->(d:Description)")
                    multi_match_where.append(
                        "d.text =~ '(?i).*{term}.*'".format(term=term))
                elif f == 'keyword':
                    multi_match.append("(n)-[:HAS_KEYWORD]->(k:Keyword)")
                    multi_match_where.append(
                        "k.term =~ '(?i).*{term}.*'".format(term=term))
                elif f == 'contributor':
                    multi_match.append("(n)-[:CONTRIBUTED_BY]->(a:Agent)")
                    multi_match_where.append(
                        "ANY(item in a.names where item =~ '(?i){term}')".format(term=term))
                else:
                    # should never be reached
                    raise RestApiException(
                        'Unexpected field type',
                        status_code=hcodes.HTTP_SERVER_ERROR)
            if len(multi_match) > 0:
                multi_match_query = "WITH n MATCH " + ', '.join(multi_match) \
                    + " WHERE " + ' OR '.join(multi_match_where)

        # check request for filtering
        filters = []
        # add filter for processed content with COMPLETE status
        # FIXME remove the following comment
        # filters.append(
        #     "MATCH (n)<-[:CREATION]-(:Item)-[:CONTENT_SOURCE]->(content:ContentStage) " +
        #     "WHERE content.status = 'COMPLETED'")
        entity = 'Creation'
        filtering = input_parameters.get('filter')
        if filtering is not None:
            # check item type
            item_type = filtering.get('type', 'all')
            if item_type is None:
                item_type = 'all'
            else:
                item_type = item_type.strip().lower()
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
            # PROVIDER
            provider = filtering.get('provider')
            if provider is not None:
                filters.append(
                    "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider)" +
                    " WHERE p.identifier='{provider}'".format(provider=provider.strip()))
            # COUNTRY
            country = filtering.get('country')
            if country is not None:
                country = country.strip().upper()
                if codelists.fromCode(country, codelists.COUNTRY) is None:
                    raise RestApiException(
                        'Invalid country code for: ' + country)
                filters.append(
                    "MATCH (n)-[:COUNTRY_OF_REFERENCE]->(c:Country) WHERE c.code='{country_ref}'".format(
                        country_ref=country))
            # IPR STATUS
            iprstatus = filtering.get('iprstatus')
            if iprstatus is not None:
                iprstatus = iprstatus.strip()
                if codelists.fromCode(iprstatus, codelists.RIGHTS_STATUS) is None:
                    raise RestApiException(
                        'Invalid IPR status code for: ' + iprstatus)
                filters.append(
                    "MATCH (n) WHERE n.rights_status = '{iprstatus}'".format(
                        iprstatus=iprstatus))
            # PRODUCTION YEAR RANGE
            year_from = filtering.get('yearfrom')
            year_to = filtering.get('yearto')
            if year_from is not None or year_to is not None:
                # set defaults if year is missing
                year_from = '1890' if year_from is None else str(year_from)
                year_to = '1999' if year_to is None else str(year_to)
                # FIXME: this DO NOT work with image
                date_clauses = []
                if item_type == 'video' or item_type == 'all':
                    date_clauses.append(
                        "ANY(item in n.production_years where item >= '{yfrom}') \
                        and ANY(item in n.production_years where item <= '{yto}')".format(
                            yfrom=year_from, yto=year_to))
                if item_type == 'image' or item_type == 'all':
                    date_clauses.append(
                        "ANY(item in n.date_created where substring(item, 0, 4) >= '{yfrom}') \
                        and ANY(item in n.date_created where substring(item, 0 , 4) <= '{yto}')".format(
                            yfrom=year_from, yto=year_to))
                filters.append("MATCH (n) WHERE {clauses}".format(
                    clauses=' or '.join(date_clauses)))
            # TERMS
            terms = filtering.get('terms')
            if terms:
                term_clauses = []
                iris = [term['iri'] for term in terms if 'iri' in term]
                if iris:
                    term_clauses.append('body.iri IN {iris}'.format(iris=iris))
                free_terms = [term['label']
                              for term in terms if 'iri' not in term and 'label' in term]
                if free_terms:
                    term_clauses.append('body.value IN {free_terms}'.format(
                        free_terms=free_terms))
                if term_clauses:
                    filters.append(
                        "MATCH (n)<-[:CREATION]-(i:Item)<-[:SOURCE]-(tag:Annotation {{annotation_type:'TAG'}})-[:HAS_BODY]-(body) \
                        WHERE {clauses}".format(
                            clauses=' or '.join(term_clauses)))

        # first request to get the number of elements to be returned
        countv = "MATCH (n:{entity})" \
            " {filters} " \
            " {match} " \
            " RETURN COUNT(DISTINCT(n))".format(
                entity=entity,
                filters=' '.join(filters),
                match=multi_match_query)

        # get total number of elements
        numels = [row[0] for row in self.graph.cypher(countv)][0]
        logger.debug("Number of elements retrieved: {0}".format(numels))

        query = "MATCH (n:{entity})" \
                " {filters} " \
                " {match} " \
                "RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
                    entity=entity,
                    filters=' '.join(filters),
                    match=multi_match_query,
                    offset=offset * limit,
                    limit=limit)
        # logger.debug(query)

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
                video['links']['thumbnail'] = video_url + \
                    '/content?type=thumbnail'
            video['links']['summary'] = video_url + '/content?type=summary'

            data.append(video)

        # return also the total number of elements
        meta_response = {"totalItems": numels}

        # count result by provider if provider == null
        if provider is None:
            count_by_provider_query = "MATCH (n:{entity})" \
                " {filters} " \
                " {match} " \
                "MATCH (n)-[:RECORD_SOURCE]->(r:RecordSource)-[:PROVIDED_BY]->(p:Provider) " \
                "WITH distinct p, count(distinct n) as numberOfCreations " \
                "RETURN p.identifier, numberOfCreations".format(
                    entity=entity,
                    filters=' '.join(filters),
                    match=multi_match_query)
            # logger.debug(count_by_provider_query)
            result_p_count = self.graph.cypher(count_by_provider_query)
            group_by_providers = {}
            for row in result_p_count:
                group_by_providers[row[0]] = row[1]
            # logger.debug(group_by_providers)
            meta_response["countByProviders"] = group_by_providers

        # count result by year
        count_by_year_query = "MATCH (n:{entity})" \
            " {filters} " \
            " {match} " \
            "WITH distinct n WITH collect(substring(head(n.production_years), 0, 3)) + collect(substring(head(n.date_created), 0, 3)) as years " \
            "UNWIND years as row " \
            "RETURN row + '0' as decade, count(row) as count order by decade".format(
                entity=entity,
                filters=' '.join(filters),
                match=multi_match_query)
        # logger.debug(count_by_year_query)
        result_y_count = self.graph.cypher(count_by_year_query)
        group_by_years = {}
        for row in result_y_count:
            group_by_years[row[0]] = row[1]
        meta_response["countByYears"] = group_by_years

        return self.force_response(data, meta=meta_response)
