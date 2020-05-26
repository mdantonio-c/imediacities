# -*- coding: utf-8 -*-

"""
Handle your video metadata
"""
from flask import send_file
from flask import request
from restapi.confs import get_api_url
from restapi.confs import PRODUCTION
from restapi.utilities.logs import log
from restapi import decorators
from restapi.exceptions import RestApiException
from restapi.utilities.htmlcodes import hcodes
from imc.apis import IMCEndpoint


#####################################
class Shots(IMCEndpoint):

    labels = ['shot']
    _GET = {'/shots/<shot_id>': {'summary': 'Gets information about a shot', 'description': 'Returns a single shot for its id', 'parameters': [{'name': 'content', 'in': 'query', 'description': 'content type (ONLY thumbnail at the moment)', 'type': 'string'}], 'responses': {'200': {'description': 'Shot information successfully retrieved'}, '401': {'description': 'This endpoint requires a valid authorization token'}, '404': {'description': 'The video does not exists.'}}}}

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    def get(self, shot_id=None):
        """
        Get shot by id.
        """
        log.debug("getting Shot id: {}", shot_id)
        if shot_id is None:
            raise RestApiException(
                "Please specify a valid shot uuid", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        self.graph = self.get_service_instance('neo4j')

        input_parameters = self.get_input()
        content_type = input_parameters['content']
        if content_type is not None and content_type != 'thumbnail':
            raise RestApiException(
                "Bad type parameter: expected 'thumbnail'",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        # check if the shot exists
        node = None
        try:
            node = self.graph.Shot.nodes.get(uuid=shot_id)
        except self.graph.Shot.DoesNotExist:
            log.debug("Shot with id {} does not exist", shot_id)
            raise RestApiException(
                "Please specify a valid shot id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        if content_type is not None:
            thumbnail_uri = node.thumbnail_uri
            log.debug("thumbnail content uri: {}", thumbnail_uri)
            if thumbnail_uri is None:
                raise RestApiException(
                    "Thumbnail not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            return send_file(thumbnail_uri, mimetype='image/jpeg')

        api_url = get_api_url(request, PRODUCTION)
        shot = self.getJsonResponse(node)
        shot['links']['self'] = api_url + 'api/shots/' + node.uuid
        shot['links']['thumbnail'] = (
            api_url + 'api/shots/' + node.uuid + '?content=thumbnail'
        )

        return self.response(shot)


class ShotAnnotations(IMCEndpoint):
    """
        Get all shot annotations for a given shot.
    """

    labels = ['shot_annotations']
    _GET = {'/shots/<shot_id>/annotations': {'summary': 'Gets shot annotations.', 'description': 'Returns all the annotations targeting the given shot.', 'parameters': [{'name': 'type', 'in': 'query', 'description': 'Filter by annotation type (e.g. TAG)', 'type': 'string', 'enum': ['TAG', 'DSC']}], 'responses': {'200': {'description': 'List of annotations.'}, '401': {'description': 'This endpoint requires a valid authorzation token.'}, '404': {'description': 'Shot does not exist.'}}}}

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @decorators.auth.required()
    def get(self, shot_id):
        log.info("get annotations for Shot id: {}", shot_id)
        if shot_id is None:
            raise RestApiException(
                "Please specify a shot id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        params = self.get_input()
        log.debug("inputs {}", params)
        anno_type = params.get('type')
        if anno_type is not None:
            anno_type = anno_type.upper()

        self.graph = self.get_service_instance('neo4j')
        data = []

        shot = None
        try:
            shot = self.graph.Shot.nodes.get(uuid=shot_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("Shot with uuid {} does not exist", shot_id)
            raise RestApiException(
                "Please specify a valid shot id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_current_user()

        for a in shot.annotation:
            if anno_type is not None and a.annotation_type != anno_type:
                continue
            if a.private:
                if a.creator is None:
                    log.warning(
                        'Invalid state: missing creator for private '
                        'note [UUID:{}]'.format(a.uuid)
                    )
                    continue
                creator = a.creator.single()
                if creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(a, max_relationship_depth=0)
            if a.annotation_type in ('TAG', 'DSC') and a.creator is not None:
                res['creator'] = self.getJsonResponse(
                    a.creator.single(), max_relationship_depth=0
                )
            # attach bodies
            res['bodies'] = []
            for b in a.bodies.all():
                anno_body = b.downcast()
                body = self.getJsonResponse(anno_body, max_relationship_depth=0)
                res['bodies'].append(body)
            data.append(res)

        return self.response(data)
