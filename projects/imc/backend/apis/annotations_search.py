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

logger = get_logger(__name__)


class SearchAnnotations(GraphBaseOperations):

    allowed_anno_types = ('TAG', 'VIM', 'TVS')

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
            filters.append('MATCH (creation:Creation)<-[:CREATION]-(i:Item)<-[:SOURCE]-(anno)')
            projections.append('collect({title:creation.identifying_title, uuid:creation.uuid}) AS creations')
            if anno_type == 'TAG':
                # look for geo distance filter
                geo_distance = filtering.get('geo_distance')
                if geo_distance is not None:
                    distance = geo_distance['distance']
                    location = geo_distance['location']
                    starters.append(
                        "WITH point({{longitude: {lon}, latitude: {lat} }}) as cityPosition, "
                        "{dist} as distanceInKm"
                        .format(lon=location['long'], lat=location['lat'], dist=distance))
                    filters.append("MATCH (anno)-[:HAS_BODY]-(body:ResourceBody) "
                                   "WHERE body.spatial IS NOT NULL AND "
                                   "distance(cityPosition, point({latitude:body.spatial[0], longitude:body.spatial[1]})) < (distanceInKm * 1000)")
                    projections.append("distance(cityPosition, point({longitude:body.spatial[0],latitude:body.spatial[1]})) as distance")
                    order_by = "ORDER BY distance"

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
                "RETURN DISTINCT body, {projections} {orderBy}".format(
                    starters=' '.join(starters),
                    filters=' '.join(filters),
                    projections=', '.join(projections),
                    orderBy=order_by)
        logger.debug(query)

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
            res['sources'] = row[1]
            res['distance'] = row[2]
            # creator = self.graph.User.inflate(row[3])
            # res['creator'] = {
            #     'uuid': creator.uuid,
            #     'name': creator.surname + ', ' + creator.name
            # }
            data.append(res)

        meta_response = {"totalItems": numels}
        return self.force_response(data, meta=meta_response)
