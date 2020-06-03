"""
Search endpoint for places

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

from restapi.confs import get_backend_url
from restapi import decorators
from restapi.exceptions import RestApiException
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log
from imc.apis import IMCEndpoint


#####################################
class SearchPlace(IMCEndpoint):

    _POST = {
        '/search_place': {
            'summary': 'Search some creations for specific place annotations',
            'description': 'Search some creations for specific place annotations.',
            'parameters': [
                {
                    'name': 'criteria',
                    'in': 'body',
                    'description': 'Criteria for the search.',
                    'schema': {
                        'required': ['relevant-list'],
                        'properties': {
                            'relevant-list': {
                                'type': 'array',
                                'items': {
                                    'required': ['creation-id', 'place-ids'],
                                    'properties': {
                                        'creation-id': {'type': 'string'},
                                        'place-ids': {
                                            'type': 'array',
                                            'items': {'type': 'string', 'minItems': 1},
                                        },
                                    },
                                },
                                'minItems': 1,
                            }
                        },
                    },
                }
            ],
            'responses': {
                '200': {'description': 'A list of creations for relevant places.'}
            },
        }
    }

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @decorators.auth.required()
    def post(self):

        self.graph = self.get_service_instance('neo4j')

        input_parameters = self.get_input()
        # at moment ONLY search for creations in a place list is available
        place_list = input_parameters.get('relevant-list')
        if place_list is None:
            raise RestApiException(
                'Only search for relevant place list allowed',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        if len(place_list) == 0:
            raise RestApiException(
                'Expected at least one relevant place list',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        data = []
        api_url = get_backend_url()
        for item in place_list:
            creation_id = item.get('creation-id')
            if creation_id is None:
                raise RestApiException(
                    'Missing creation-id', status_code=hcodes.HTTP_BAD_REQUEST
                )
            place_ids = item.get('place-ids')
            if place_ids is None or len(place_ids) == 0:
                raise RestApiException(
                    'Missing place-ids', status_code=hcodes.HTTP_BAD_REQUEST
                )
            query = (
                "MATCH (n:Creation {{uuid:'{uuid}'}}) "
                "MATCH (n)<-[:CREATION]-(i:Item)<-[:SOURCE]-(anno:Annotation {{annotation_type:'TAG'}})-[:HAS_BODY]-(body:ResourceBody) "
                "WHERE body.iri IN {place_ids} "
                "MATCH (n)-[:HAS_TITLE]->(title:Title) "
                "MATCH (anno)-[:IS_ANNOTATED_BY]-(c:User) "
                "MATCH (n)-[:RECORD_SOURCE]->(:RecordSource)-[:PROVIDED_BY]->(p:Provider) "
                "OPTIONAL MATCH (anno)-[:HAS_TARGET]-(target:Shot) "
                "OPTIONAL MATCH (i)-[:REVISION_BY]-(r:User) "
                "WITH n, collect(distinct title) AS titles, p,"
                " i, anno, body, target AS shot, c{{.uuid, .name, .surname, .email}} AS creator, r{{.uuid, .name, .surname}} AS reviser "
                "RETURN n{{.*, type:i.item_type, titles, provider:p.identifier, reviser:reviser}}, collect(anno{{.*, body, shot, creator}})".format(
                    uuid=creation_id, place_ids=place_ids
                )
            )
            log.debug(query)
            result = self.graph.cypher(query)
            for row in result:
                creation_uuid = row[0]['uuid']
                creation_type = row[0]['type']
                creation = {
                    'uuid': creation_uuid,
                    'external_ids': row[0]['external_ids'],
                    'rights_status': row[0]['rights_status'],
                    'type': creation_type,
                    'provider': row[0]['provider'],
                    'reviser': row[0]['reviser'],
                }
                # add some useful links
                if creation_type == 'Video':
                    creation['links'] = {}
                    creation['links']['content'] = (
                        api_url + '/api/videos/' + creation_uuid + '/content?type=video'
                    )
                    creation['links']['thumbnail'] = (
                        api_url
                        + '/api/videos/'
                        + creation_uuid
                        + '/content?type=thumbnail'
                    )
                elif creation_type == 'Image':
                    creation['links'] = {}
                    creation['links']['content'] = (
                        api_url + '/api/images/' + creation_uuid + '/content?type=video'
                    )
                    creation['links']['thumbnail'] = (
                        api_url
                        + '/api/images/'
                        + creation_uuid
                        + '/content?type=thumbnail'
                    )
                # PRODUCTION YEAR: get the first year in the array
                if 'production_years' in row[0]:
                    creation['year'] = row[0]['production_years'][0]
                elif 'date_created' in row[0]:
                    creation['year'] = row[0]['date_created'][0]
                # TITLE
                if 'identifying_title' in row[0]:
                    creation['title'] = row[0]['identifying_title']
                elif 'titles' in row[0] and len(row[0]['titles']) > 0:
                    for t in row[0]['titles']:
                        title_node = self.graph.Title.inflate(t)
                        title = title_node.text
                        if (
                            title_node.language is not None
                            and title_node.language == 'en'
                        ):
                            break
                    creation['title'] = title
                annotations = []
                for col in row[1]:
                    anno = {
                        'uuid': col['uuid'],
                        'creation_datetime': col['creation_datetime'],
                        'annotation_type': col['annotation_type'],
                        'creator': col['creator'],
                    }
                    body = self.graph.ResourceBody.inflate(col['body'])
                    anno['body'] = {
                        'iri': body.iri,
                        'name': body.name,
                        'spatial': body.spatial,
                    }
                    if col['shot'] is not None:
                        shot = self.graph.Shot.inflate(col['shot'])
                        anno['shot'] = {
                            'uuid': shot.uuid,
                            'duration': shot.duration,
                            'shot_num': shot.shot_num,
                            'start_frame_idx': shot.start_frame_idx,
                            'end_frame_idx': shot.end_frame_idx,
                            'timestamp': shot.timestamp,
                        }
                    annotations.append(anno)
                res = {'source': creation, 'annotations': annotations}
                data.append(res)

        return self.response(data)
