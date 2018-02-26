# -*- coding: utf-8 -*-

"""
Search endpoint for annotations
"""

from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from imc.models import codelists

logger = get_logger(__name__)


class SearchAnnotations(GraphBaseOperations):

    allowed_anno_types = ('TAG', 'VIM', 'TVS')
    allowed_item_types = ('all', 'video', 'image', 'text')
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

        filters = []
        starters = []
        projections = []
        order_by = ''
        filtering = input_parameters.get('filter')
        if filtering is not None:
            anno_type = filtering.get('type')
            if anno_type is None:
                raise RestApiException('Annotation type cannot be empty',
                                       status_code=hcodes.HTTP_BAD_REQUEST)
            if anno_type not in self.__class__.allowed_anno_types:
                raise RestApiException(
                    "Bad annotation type parameter: expected one of %s" %
                    (self.__class__.allowed_anno_types, ),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            filters.append("WHERE anno.annotation_type='{anno_type}'".format(
                anno_type=anno_type))
            # add filter for processed content with COMPLETE status
            filters.append(
                "MATCH (creation:Creation)<-[:CREATION]-(:Item)-[:CONTENT_SOURCE]->(content:ContentStage) " +
                "WHERE content.status = 'COMPLETED' ")
            filters.append(
                'MATCH (title:Title)<-[:HAS_TITLE]-(creation)<-[:CREATION]-(i:Item)<-[:SOURCE]-(anno)')
            projections.append(
                'collect(distinct creation{.*, type:i.item_type, titles }) AS creations')
            if anno_type == 'TAG':
                # look for geo distance filter
                geo_distance = filtering.get('geo_distance')
                if geo_distance is not None:
                    distance = geo_distance['distance']
                    location = geo_distance['location']
                    starters.append(
                        "WITH point({{longitude: {lon}, latitude: {lat} }}) as cityPosition, "
                        "{dist} as distanceInMeters"
                        .format(lon=location['long'], lat=location['lat'], dist=distance))
                    filters.append("MATCH (anno)-[:HAS_BODY]-(body:ResourceBody) "
                                   "WHERE body.spatial IS NOT NULL AND "
                                   "distance(cityPosition, point({latitude:body.spatial[0], longitude:body.spatial[1]})) < distanceInMeters")
                    projections.append(
                        "distance(cityPosition, point({longitude:body.spatial[0],latitude:body.spatial[1]})) as distance")
                    order_by = "ORDER BY distance"
            creation = filtering.get('creation')
            if creation is not None:
                c_match = creation.get('match')
                if c_match is not None:
                    term = c_match.get('term', '').strip()
                    if not term:
                        raise RestApiException('Term input cannot be empty',
                                               status_code=hcodes.HTTP_BAD_REQUEST)
                    multi_match = []
                    multi_match_where = []
                    multi_match_query = ''
                    # clean up term from '*'
                    term = term.replace("*", "")

                    fields = c_match.get('fields')
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
                            multi_match.append(
                                "(creation)-[:HAS_TITLE]->(t:Title)")
                            multi_match_where.append(
                                "t.text =~ '(?i).*{term}.*'".format(term=term))
                        elif f == 'description':
                            multi_match.append(
                                "(creation)-[:HAS_DESCRIPTION]->(d:Description)")
                            multi_match_where.append(
                                "d.text =~ '(?i).*{term}.*'".format(term=term))
                        elif f == 'keyword':
                            multi_match.append(
                                "(creation)-[:HAS_KEYWORD]->(k:Keyword)")
                            multi_match_where.append(
                                "k.term =~ '(?i){term}'".format(term=term))
                        elif f == 'contributor':
                            multi_match.append(
                                "(creation)-[:CONTRIBUTED_BY]->(a:Agent)")
                            multi_match_where.append(
                                "ANY(item in a.names where item =~ '(?i).*{term}.*')".format(term=term))
                        else:
                            # should never be reached
                            raise RestApiException(
                                'Unexpected field type',
                                status_code=hcodes.HTTP_SERVER_ERROR)
                    if len(multi_match) > 0:
                        multi_match_query = "MATCH " + ', '.join(multi_match) \
                            + " WHERE " + ' OR '.join(multi_match_where)
                        # logger.debug(multi_match_query)
                        filters.append(multi_match_query)

                c_filter = creation.get('filter')
                # TYPE
                c_type = c_filter.get('type', 'all')
                c_type = c_type.strip().lower()
                if c_type not in self.__class__.allowed_item_types:
                    raise RestApiException(
                        "Bad item type parameter: expected one of %s" %
                        (self.__class__.allowed_item_types, ),
                        status_code=hcodes.HTTP_BAD_REQUEST)
                if c_type != 'all':
                    filters.append("MATCH (i) WHERE i.item_type =~ '(?i){c_type}'"
                                   .format(c_type=c_type))
                # IPR STATUS
                c_iprstatus = c_filter.get('iprstatus')
                if c_iprstatus is not None:
                    c_iprstatus = c_iprstatus.strip()
                    if codelists.fromCode(c_iprstatus, codelists.RIGHTS_STATUS) is None:
                        raise RestApiException(
                            'Invalid IPR status code for: ' + c_iprstatus)
                    filters.append(
                        "MATCH (creation) WHERE creation.rights_status = '{iprstatus}'".format(
                            iprstatus=c_iprstatus))
                # PRODUCTION YEAR
                c_year_from = c_filter.get('yearfrom')
                c_year_to = c_filter.get('yearto')
                if c_year_from is not None or c_year_to is not None:
                    # set defaults if year is missing
                    c_year_from = '1890' if c_year_from is None else str(
                        c_year_from)
                    c_year_to = '1999' if c_year_to is None else str(c_year_to)
                    date_clauses = []
                    if c_type == 'video' or c_type == 'all':
                        date_clauses.append(
                            "ANY(item IN creation.production_years WHERE item >= '{yfrom}') \
                            and ANY(item IN creation.production_years WHERE item <= '{yto}')".format(
                                yfrom=c_year_from, yto=c_year_to))
                    if c_type == 'image' or c_type == 'text' or c_type == 'all':
                        date_clauses.append(
                            "ANY(item IN creation.date_created WHERE substring(item, 0, 4) >= '{yfrom}') \
                            and ANY(item IN creation.date_created WHERE substring(item, 0 , 4) <= '{yto}')".format(
                                yfrom=c_year_from, yto=c_year_to))
                    filters.append("MATCH (creation) WHERE {clauses}".format(
                        clauses=' or '.join(date_clauses)))
                # ANNOTATED TERMS
                terms = c_filter.get('terms')
                if terms:
                    term_clauses = []
                    iris = [term['iri'] for term in terms if 'iri' in term]
                    if iris:
                        term_clauses.append(
                            'term.iri IN {iris}'.format(iris=iris))
                    free_terms = [term['label']
                                  for term in terms if 'iri' not in term and 'label' in term]
                    if free_terms:
                        term_clauses.append('term.value IN {free_terms}'.format(
                            free_terms=free_terms))
                    if term_clauses:
                        filters.append(
                            "MATCH (i)<-[:SOURCE]-(anno2)-[:HAS_BODY]-(term) WHERE {clauses}"
                            .format(
                                clauses=' or '.join(term_clauses)))

        # first request to get the number of elements to be returned
        countv = "{starters} MATCH (anno:Annotation)" \
            " {filters} " \
            " RETURN COUNT(DISTINCT body)".format(
                starters=' '.join(starters),
                filters=' '.join(filters))

        # get total number of elements
        numels = [row[0] for row in self.graph.cypher(countv)][0]
        logger.debug("Number of elements retrieved: {0}".format(numels))

        query = "{starters} MATCH (anno:Annotation)" \
                " {filters} " \
                "WITH body, i, cityPosition, creation, collect(distinct title) AS titles " \
                "RETURN DISTINCT body, {projections} {orderBy}".format(
                    starters=' '.join(starters),
                    filters=' '.join(filters),
                    projections=', '.join(projections),
                    orderBy=order_by)
        # logger.debug(query)

        data = []
        result = self.graph.cypher(query)
        for row in result:
            # AD-HOC implementation at the moment
            body = self.graph.ResourceBody.inflate(row[0])
            res = {
                'iri': body.iri,
                'name': body.name,
                'spatial': body.spatial
            }
            res['sources'] = []
            for source in row[1]:
                creation = {
                    'uuid': source['uuid'],
                    'external_ids': source['external_ids'],
                    'rights_status': source['rights_status'],
                    'type': source['type']
                }
                # PRODUCTION YEAR: get the first year in the array
                if 'production_years' in source:
                    creation['year'] = source['production_years'][0]
                elif 'date_created' in source:
                    creation['year'] = source['date_created'][0]
                # TITLE
                if 'identifying_title' in source:
                    creation['title'] = source['identifying_title']
                elif 'titles' in source and len(source['titles']) > 0:
                    # at the moment get the first always!
                    title_node = self.graph.Title.inflate(source['titles'][0])
                    creation['title'] = title_node.text
                res['sources'].append(creation)

            res['distance'] = row[2]
            # creator = self.graph.User.inflate(row[3])
            # res['creator'] = {
            #     'uuid': creator.uuid,
            #     'name': creator.surname + ', ' + creator.name
            # }
            data.append(res)

        meta_response = {"totalItems": numels}
        return self.force_response(data, meta=meta_response)
