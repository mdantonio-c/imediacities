# -*- coding: utf-8 -*-

"""
Handle annotations
"""

from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities.logs import get_logger
from utilities import htmlcodes as hcodes
# from imc.tasks.services.xml_result_parser import XMLResultParser
from imc.tasks.services.annotation_repository import AnnotationRepository

import re
TARGET_PATTERN = re.compile("(item|shot|anno):([a-z0-9-])+")
SELECTOR_PATTERN = re.compile("t=\d+,\d+")

logger = get_logger(__name__)


#####################################
class Annotations(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, anno_id=None):
        """Get an annotation if its id is passed as an argument."""
        self.initGraph()

        params = self.get_input()
        logger.debug('input: {}'.format(params))
        type_f = params['type']
        if type_f is not None:
            type_f = type_f.upper()

        if anno_id is not None:
            # check if the video exists
            try:
                anno = self.graph.Annotation.nodes.get(uuid=anno_id)
            except self.graph.Annotation.DoesNotExist:
                logger.debug(
                    "Annotation with uuid %s does not exist" % anno_id)
                raise RestApiException(
                    "Please specify a valid annotation id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            annotations = [anno]
        elif type_f is not None:
            annotations = self.graph.Annotation.nodes.filter(
                annotation_type=type_f)
        else:
            annotations = self.graph.Annotation.nodes.all()

        data = []
        for a in annotations:
            anno = self.getJsonResponse(a)
            data.append(anno)

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):
        """Create a new annotation."""
        data = self.get_input()
        # logger.debug(data)
        if len(data) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)
        if 'target' not in data:
            raise RestApiException(
                'Target is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)
        if 'body' not in data:
            raise RestApiException(
                'Body is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)
        # check the target
        target = data['target']
        logger.debug('Annotate target: {}'.format(target))
        if not TARGET_PATTERN.match(target):
            raise RestApiException(
                'Invalid Target format',
                status_code=hcodes.HTTP_BAD_REQUEST)
        target_type, tid = target.split(':')
        logger.debug('target type: {}, target id: {}'.format(
            target_type, tid))

        self.initGraph()

        # check user
        user = self._current_user
        if user is None:
            raise RestApiException(
                'Invalid user',
                status_code=hcodes.HTTP_BAD_REQUEST)

        targetNode = None
        if target_type == 'item':
            targetNode = self.graph.Item.nodes.get_or_none(uuid=tid)
        elif target_type == 'shot':
            targetNode = self.graph.Shot.nodes.get_or_none(uuid=tid)
        elif target_type == 'anno':
            targetNode = self.graph.Annotation.nodes.get_or_none(uuid=tid)
        else:
            # this should never be reached
            raise RestApiException(
                'Invalid target type',
                status_code=hcodes.HTTP_SERVER_ERROR)

        if targetNode is None:
            raise RestApiException(
                'Target [' + target_type + '][' + tid + '] does not exist',
                status_code=hcodes.HTTP_BAD_REQUEST)

        # check the selector
        selector = data.get('selector', None)
        logger.debug('selector: {}'.format(selector))
        if selector is not None:
            if selector['type'] != 'FragmentSelector':
                raise RestApiException(
                    'Invalid selector type for: ' + selector['type'],
                    status_code=hcodes.HTTP_BAD_REQUEST)
            s_val = selector['value']
            if s_val is None or not SELECTOR_PATTERN.match(s_val):
                raise RestApiException(
                    'Invalid selector value for: ' + s_val,
                    status_code=hcodes.HTTP_BAD_REQUEST)

        # check body
        body = data['body']
        b_type = body.get('type')
        if b_type == 'ResourceBody':
            source = body.get('source')
            if source is None:
                raise RestApiException(
                    'Missing Source in the ResourceBody',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            # here we expect the source as an IRI or a structured object
            # 1) just the IRI
            if isinstance(source, str):
                pass
            # 2) structured object
            elif 'iri' not in source or 'name' not in source:
                raise RestApiException(
                    'Invalid ResourceBody',
                    status_code=hcodes.HTTP_BAD_REQUEST)
        elif b_type == 'TextualBody':
            if 'value' not in body or 'language' not in body:
                raise RestApiException(
                    'Invalid TextualBody',
                    status_code=hcodes.HTTP_BAD_REQUEST)
        else:
            raise RestApiException('Invalid body type for: {}'.format(b_type))

        # create manual annotation
        repo = AnnotationRepository(self.graph)
        repo.create_manual_annotation(user, body, targetNode, selector)

        return self.force_response("", code=hcodes.HTTP_OK_CREATED)

    @decorate.catch_error()
    @catch_graph_exceptions
    def delete(self, anno_id):
        """ Deletes an annotaion."""
        if anno_id is None:
            raise RestApiException(
                "Please specify an annotation id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()

        anno = self.getNode(self.graph.Annotation, anno_id, field='uuid')
        if anno is None:
            raise RestApiException(
                'Annotation not found',
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        repo = AnnotationRepository(self.graph)
        repo.delete_manual_annotation(anno)

        return self.empty_response()
