# -*- coding: utf-8 -*-

"""
Search endpoint

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

from flask import request
from restapi.confs import get_api_url
from restapi.confs import PRODUCTION

from restapi.utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.exceptions import RestApiException
from restapi.utilities.htmlcodes import hcodes
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.decorators import catch_graph_exceptions
from imc.models import codelists

log = get_logger(__name__)


#####################################
class Search(GraphBaseOperations):

    labels = ['file']
    POST = {'/search': {'summary': 'Search some videos', 'description': 'Search videos previously staged in the area.', 'parameters': [{'name': 'criteria', 'in': 'body', 'description': 'Criteria for the search.', 'schema': {'$ref': '#/definitions/SearchCriteria'}}, {'name': 'perpage', 'in': 'query', 'description': 'Number of videos returned', 'type': 'integer'}, {'name': 'currentpage', 'in': 'query', 'description': 'Page number', 'type': 'integer'}], 'responses': {'200': {'description': 'A list of videos matching search criteria.'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}

    allowed_item_types = ('all', 'video', 'image')  # , 'text')
    allowed_term_fields = ('title', 'description', 'keyword', 'contributor')
    allowed_anno_types = ('TAG', 'DSC', 'LNK')

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.graph = self.get_service_instance('neo4j')

        user = self.get_user_if_logged()
        input_parameters = self.get_input()
        offset, limit = self.get_paging()
        offset -= 1
        log.debug("paging: offset {0}, limit {1}".format(offset, limit))
        if offset < 0:
            raise RestApiException(
                'Page number cannot be a negative value',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        if limit < 0:
            raise RestApiException(
                'Page size cannot be a negative value',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        # check request for term matching
        provider = None

        # TODO: no longer used, to be removed
        multi_match_query = ''

        # multi_match = []
        # multi_match_where = []
        # match = input_parameters.get('match')

        # if match is not None:
        #     term = match.get('term')
        #     if term is not None:
        #         term = self.graph.sanitize_input(term)

        #     fields = match.get('fields')
        #     if term is not None and (fields is None or len(fields) == 0):
        #         raise RestApiException('Match term fields cannot be empty',
        #                                status_code=hcodes.HTTP_BAD_REQUEST)
        #     if fields is None:
        #         fields = []
        #     multi_match_fields = []
        #     multi_optional_match = []
        #     for f in fields:
        #         if f not in self.__class__.allowed_term_fields:
        #             raise RestApiException(
        #                 "Bad field: expected one of %s" %
        #                 (self.__class__.allowed_term_fields, ),
        #                 status_code=hcodes.HTTP_BAD_REQUEST)
        #         if not term:
        #             # catch '*'
        #             break
        #         if f == 'title':
        #             multi_match.append("MATCH (n)-[:HAS_TITLE]->(t:Title)")
        #             multi_match_fields.append('t')
        #             multi_match_where.append(
        #                 "t.text =~ '(?i).*{term}.*'".format(term=term))
        #         elif f == 'description':
        #             multi_match.append(
        #                 "OPTIONAL MATCH (n)-[:HAS_DESCRIPTION]->(d:Description)")
        #             multi_match_fields.append('d')
        #             multi_match_where.append(
        #                 "d.text =~ '(?i).*{term}.*'".format(term=term))
        #         elif f == 'keyword':
        #             multi_optional_match.append("OPTIONAL MATCH (n)-[:HAS_KEYWORD]->(k:Keyword)")
        #             multi_match_fields.append('k')
        #             multi_match_where.append(
        #                 "k.term =~ '(?i){term}'".format(term=term))
        #         elif f == 'contributor':
        #             multi_optional_match.append("OPTIONAL MATCH (n)-[:CONTRIBUTED_BY]->(a:Agent)")
        #             multi_match_fields.append('a')
        #             multi_match_where.append(
        #                 "ANY(item in a.names where item =~ '(?i).*{term}.*')".format(term=term))
        #         else:
        #             # should never be reached
        #             raise RestApiException(
        #                 'Unexpected field type',
        #                 status_code=hcodes.HTTP_SERVER_ERROR)
        #     if len(multi_match) > 0:
        #         multi_match_query = ' '.join(multi_match) \
        #             + " " + ' '.join(multi_optional_match) \
        #             + " WITH n, " + ', '.join(multi_match_fields) \
        #             + " WHERE " + ' OR '.join(multi_match_where)

        # check request for filtering
        filters = []
        # add filter for processed content with COMPLETE status
        filters.append(
            "MATCH (n)<-[:CREATION]-(:Item)-[:CONTENT_SOURCE]->(content:ContentStage) "
            + "WHERE content.status = 'COMPLETED'"
        )
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
                    "Bad item type parameter: expected one of %s"
                    % (self.__class__.allowed_item_types,),
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            if item_type == 'all':
                entity = 'Creation'
            elif item_type == 'video':
                entity = 'AVEntity'
            elif item_type == 'image':
                entity = 'NonAVEntity'
            else:
                # should never be reached
                raise RestApiException(
                    'Unexpected item type', status_code=hcodes.HTTP_SERVER_ERROR
                )
            # PROVIDER
            provider = filtering.get('provider')
            log.debug("provider {0}".format(provider))
            # if provider is not None:
            #    filters.append(
            #        "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider)" +
            #        " WHERE p.identifier='{provider}'".format(provider=provider.strip()))
            # CITY
            city = filtering.get('city')
            if city is not None:
                filters.append(
                    "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider)"
                    + " WHERE p.city='{city}'".format(city=city.strip())
                )
            log.debug("city {0}".format(city))
            # COUNTRY
            country = filtering.get('country')
            if country is not None:
                country = country.strip().upper()
                if codelists.fromCode(country, codelists.COUNTRY) is None:
                    raise RestApiException('Invalid country code for: ' + country)
                filters.append(
                    "MATCH (n)-[:COUNTRY_OF_REFERENCE]->(c:Country) WHERE c.code='{country_ref}'".format(
                        country_ref=country
                    )
                )
            # IPR STATUS
            iprstatus = filtering.get('iprstatus')
            if iprstatus is not None:
                iprstatus = iprstatus.strip()
                if codelists.fromCode(iprstatus, codelists.RIGHTS_STATUS) is None:
                    raise RestApiException('Invalid IPR status code for: ' + iprstatus)
                filters.append(
                    "MATCH (n) WHERE n.rights_status = '{iprstatus}'".format(
                        iprstatus=iprstatus
                    )
                )
            # PRODUCTION YEAR RANGE
            missingDate = filtering.get('missingDate')
            # log.debug("missingDate: {0}".format(missingDate))
            if not missingDate:
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
                            "ANY(item in n.production_years where item >= '{yfrom}') "
                            "and ANY(item in n.production_years where item <= '{yto}')".format(
                                yfrom=year_from, yto=year_to
                            )
                        )
                    if item_type == 'image' or item_type == 'all':
                        date_clauses.append(
                            "ANY(item in n.date_created where substring(item, 0, 4) >= '{yfrom}') "
                            "and ANY(item in n.date_created where substring(item, 0 , 4) <= '{yto}')".format(
                                yfrom=year_from, yto=year_to
                            )
                        )
                    filters.append(
                        "MATCH (n) WHERE {clauses}".format(
                            clauses=' or '.join(date_clauses)
                        )
                    )
            # TERMS
            terms = filtering.get('terms')
            if terms:
                term_clauses = []
                iris = [
                    term['iri']
                    for term in terms
                    if 'iri' in term and term['iri'] is not None
                ]
                if iris:
                    term_clauses.append('body.iri IN {iris}'.format(iris=iris))
                free_terms = [
                    term['label']
                    for term in terms
                    if 'iri' not in term or term['iri'] is None and 'label' in term
                ]
                if free_terms:
                    term_clauses.append(
                        'body.value IN {free_terms}'.format(free_terms=free_terms)
                    )
                if term_clauses:
                    filters.append(
                        "MATCH (n)<-[:CREATION]-(i:Item)<-[:SOURCE]-(tag:Annotation {{annotation_type:'TAG'}})-[:HAS_BODY]-(body) "
                        "WHERE {clauses}".format(clauses=' or '.join(term_clauses))
                    )
            # ANNOTATED BY
            annotated_by = filtering.get('annotated_by')
            # if no user ignore this filter
            if user and annotated_by:
                # only annotated *BY ME* is autorized (except for the admin)
                anno_user_id = annotated_by.get('user', None)
                if anno_user_id is None:
                    raise RestApiException(
                        'Missing user in annotated_by filter',
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
                iamadmin = self.auth.verify_admin()
                if user.uuid != anno_user_id and not iamadmin:
                    raise RestApiException(
                        'You are not allowed to search for item that are not annotated by you',
                        status_code=hcodes.HTTP_BAD_FORBIDDEN,
                    )
                if iamadmin:
                    # check if 'user' in annotated_by filter exists
                    try:
                        v = self.graph.User.nodes.get(uuid=anno_user_id)
                    except self.graph.User.DoesNotExist:
                        log.debug("User with uuid %s does not exist" % anno_user_id)
                        raise RestApiException(
                            "Please specify a valid user id in annotated_by filter",
                            status_code=hcodes.HTTP_BAD_NOTFOUND,
                        )
                anno_type = annotated_by.get('type', 'TAG')
                if anno_type not in self.__class__.allowed_anno_types:
                    raise RestApiException(
                        "Bad annotation type in annotated_by filter: expected one of %s"
                        % (self.__class__.allowed_anno_types,),
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
                filters.append(
                    "MATCH (n)<-[:CREATION]-(i:Item)<-[:SOURCE]-(tag:Annotation {{annotation_type:'{type}'}})"
                    "-[IS_ANNOTATED_BY]->(:User {{uuid:'{user}'}})".format(
                        user=anno_user_id, type=anno_type
                    )
                )

        match = input_parameters.get('match')
        fulltext = None
        if match is not None:

            term = match.get('term')
            if term is not None:
                term = self.graph.sanitize_input(term)
                term = self.graph.fuzzy_tokenize(term)

            # Create with:
            # CALL db.index.fulltext.createNodeIndex("titles",["Title", "Description", "Keyword"],["text", "term"])

            fulltext = """
                CALL db.index.fulltext.queryNodes("titles", '{term}')
                YIELD node, score
                WITH node, score
                MATCH (n:{entity})-[:HAS_TITLE|HAS_DESCRIPTION|HAS_KEYWORD]->(node)
            """.format(
                term=term, entity=entity
            )
            # RETURN node, n, score

        # first request to get the number of elements to be returned
        if fulltext is not None:
            countv = "{fulltext} {filters} RETURN COUNT(DISTINCT(n))".format(
                fulltext=fulltext, filters=' '.join(filters)
            )
            query = (
                "{fulltext} {filters} "
                "RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
                    fulltext=fulltext,
                    filters=' '.join(filters),
                    offset=offset * limit,
                    limit=limit,
                )
            )

        else:
            countv = (
                "MATCH (n:{entity})"
                " {filters} "
                " {match} "
                " RETURN COUNT(DISTINCT(n))".format(
                    entity=entity, filters=' '.join(filters), match=multi_match_query
                )
            )
            query = (
                "MATCH (n:{entity})"
                " {filters} "
                " {match} "
                "RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
                    entity=entity,
                    filters=' '.join(filters),
                    match=multi_match_query,
                    offset=offset * limit,
                    limit=limit,
                )
            )

        # log.debug("QUERY to get number of elements: {0}".format(countv))

        data = []
        meta_response = {"totalItems": 0, "countByProviders": 0, "countByYears": 0}
        # get total number of elements
        try:
            numels = [row[0] for row in self.graph.cypher(countv)][0]
        except BaseException as e:
            log.error(e)
            return self.force_response(
                data, meta=meta_response, errors=['Invalid query parameters']
            )
            raise RestApiException('Invalid query parameters')

        log.debug("Number of elements retrieved: {0}".format(numels))

        # return also the total number of elements
        meta_response["totalItems"] = numels
        # log.debug(query)

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
                    'Unexpected item type', status_code=hcodes.HTTP_SERVER_ERROR
                )

            item = v.item.single()

            if isinstance(v, self.graph.AVEntity):
                # video
                video_url = api_url + 'api/videos/' + v.uuid
                video = self.getJsonResponse(
                    v,
                    max_relationship_depth=1,
                    relationships_expansion=[
                        'record_sources.provider',
                        'item.ownership',
                        'item.revision',
                    ],
                )
                log.debug("video links %s" % video['links'])
                video['links']['self'] = video_url
                video['links']['content'] = video_url + '/content?type=video'
                if item.thumbnail is not None:
                    video['links']['thumbnail'] = video_url + '/content?type=thumbnail'
                video['links']['summary'] = video_url + '/content?type=summary'
                data.append(video)
            elif isinstance(v, self.graph.NonAVEntity):
                # image
                image_url = api_url + 'api/images/' + v.uuid
                image = self.getJsonResponse(
                    v,
                    max_relationship_depth=1,
                    relationships_expansion=[
                        'record_sources.provider',
                        'item.ownership',
                        # 'titles.creation',
                        # 'keywords.creation',
                        # 'descriptions.creation',
                    ],
                )
                log.debug("image links %s" % image['links'])
                image['links']['self'] = image_url
                image['links']['content'] = image_url + '/content?type=image'
                if item.thumbnail is not None:
                    image['links']['thumbnail'] = image_url + '/content?type=thumbnail'
                image['links']['summary'] = image_url + '/content?type=summary'
                data.append(image)

        # count result by provider if provider == null
        if provider is None:
            count_by_provider_query = (
                "MATCH (n:{entity})"
                " {filters} "
                " {match} "
                "MATCH (n)-[:RECORD_SOURCE]->(r:RecordSource)-[:PROVIDED_BY]->(p:Provider) "
                "WITH distinct p, count(distinct n) as numberOfCreations "
                "RETURN p.identifier, numberOfCreations".format(
                    entity=entity, filters=' '.join(filters), match=multi_match_query
                )
            )
            # log.debug(count_by_provider_query)
            result_p_count = self.graph.cypher(count_by_provider_query)
            group_by_providers = {}
            for row in result_p_count:
                group_by_providers[row[0]] = row[1]
            # log.debug(group_by_providers)
            meta_response["countByProviders"] = group_by_providers

        # count result by year
        count_by_year_query = (
            "MATCH (n:{entity})"
            " {filters} "
            " {match} "
            "WITH distinct n WITH collect(substring(head(n.production_years), 0, 3)) + collect(substring(head(n.date_created), 0, 3)) as years "
            "UNWIND years as row "
            "RETURN row + '0' as decade, count(row) as count order by decade".format(
                entity=entity, filters=' '.join(filters), match=multi_match_query
            )
        )
        # log.debug(count_by_year_query)
        result_y_count = self.graph.cypher(count_by_year_query)
        group_by_years = {}
        for row in result_y_count:
            group_by_years[row[0]] = row[1]
        meta_response["countByYears"] = group_by_years

        return self.force_response(data, meta=meta_response)
