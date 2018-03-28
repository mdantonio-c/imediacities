# -*- coding: utf-8 -*-

"""
Search endpoint for places

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
class SearchPlace(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):

        self.initGraph()

        input_parameters = self.get_input()
        # at moment ONLY search for creations in a place list is available
        place_list = input_parameters.get('relevant-list')
        if place_list is None:
            raise RestApiException('Only search for relevant place list allowed',
                                   status_code=hcodes.HTTP_BAD_REQUEST)
        if len(place_list) == 0:
            raise RestApiException('Expected at least one relevant place list',
                                   status_code=hcodes.HTTP_BAD_REQUEST)
        data = []
        api_url = get_api_url(request, PRODUCTION)
        for item in place_list:
            creation_id = item.get('creation-id')
            if creation_id is None:
                raise RestApiException('Missing creation-id',
                                       status_code=hcodes.HTTP_BAD_REQUEST)
            place_ids = item.get('place-ids')
            if place_ids is None or len(place_ids) == 0:
                raise RestApiException('Missing place-ids',
                                       status_code=hcodes.HTTP_BAD_REQUEST)
            # logger.debug('creation: {}, places: {}'.format(creation_id, place_ids))
            query = "MATCH (n:Creation {{uuid:'{uuid}'}}) " \
                "MATCH (n)<-[:CREATION]-(i:Item)<-[:SOURCE]-(anno:Annotation {{annotation_type:'TAG'}})-[:HAS_BODY]-(body:ResourceBody) " \
                "WHERE body.iri IN {place_ids} " \
                "MATCH (n)-[:HAS_TITLE]->(title:Title) " \
                "MATCH (anno)-[:IS_ANNOTATED_BY]-(c:User) " \
                "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider) " \
                "OPTIONAL MATCH (anno)-[:HAS_TARGET]-(target:Shot) " \
                "WITH n, collect(distinct title) AS titles, p," \
                " i, anno, body, target AS shot, c{{.uuid, .name, .surname, .email}} AS creator " \
                "RETURN n{{.*, type:i.item_type, titles, provider:p.identifier}}, collect(anno{{.*, body, shot, creator}})".format(
                    uuid=creation_id, place_ids=place_ids)
            result = self.graph.cypher(query)
            for row in result:
                creation = {
                    'uuid': row[0]['uuid'],
                    'external_ids': row[0]['external_ids'],
                    'rights_status': row[0]['rights_status'],
                    'type': row[0]['type'],
                    'provider': row[0]['provider'],
                    'links': {
                        'content': api_url + 'api/videos/' + row[0]['uuid'] + '/content?type=video',
                        'thumbnail': api_url + 'api/videos/' + row[0]['uuid'] + '/content?type=thumbnail',
                    }
                }
                # PRODUCTION YEAR: get the first year in the array
                if 'production_years' in row[0]:
                    creation['year'] = row[0]['production_years'][0]
                elif 'date_created' in row[0]:
                    creation['year'] = row[0]['date_created'][0]
                # TITLE
                if 'identifying_title' in row[0]:
                    creation['title'] = row[0]['identifying_title']
                elif 'titles' in row[0] and len(row[0]['titles']) > 0:
                    # at the moment get the first always!
                    title_node = self.graph.Title.inflate(row[0]['titles'][0])
                    creation['title'] = title_node.text
                annotations = []
                for col in row[1]:
                    anno = {
                        'uuid': col['uuid'],
                        'creation_datetime': col['creation_datetime'],
                        'annotation_type': col['annotation_type'],
                        'creator': col['creator']
                    }
                    body = self.graph.ResourceBody.inflate(col['body'])
                    anno['body'] = {
                        'iri': body.iri,
                        'name': body.name,
                        'spatial': body.spatial
                    }
                    if col['shot'] is not None:
                        shot = self.graph.Shot.inflate(col['shot'])
                        anno['shot'] = {
                            'uuid': shot.uuid,
                            'duration': shot.duration,
                            'shot_num': shot.shot_num,
                            'start_frame_idx': shot.start_frame_idx,
                            'end_frame_idx': shot.end_frame_idx,
                            'timestamp': shot.timestamp
                        }
                    annotations.append(anno)
                res = {
                    'source': creation,
                    'annotations': annotations
                }
                data.append(res)

        return self.force_response(data)
