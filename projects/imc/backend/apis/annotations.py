# -*- coding: utf-8 -*-

"""
Handle annotations
"""

from flask import request
from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities.logs import get_logger
from utilities import htmlcodes as hcodes
# from imc.tasks.services.xml_result_parser import XMLResultParser
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.tasks.services.annotation_repository import DuplicatedAnnotationError

import datetime
import re
TARGET_PATTERN = re.compile("(item|shot|anno):([a-z0-9-])+")
BODY_PATTERN = re.compile("(resource|textual):.+")
SELECTOR_PATTERN = re.compile("t=\d+,\d+")

logger = get_logger(__name__)

__author__ = "Giuseppe Trotta(g.trotta@cineca.it)"


#####################################
class Annotations(GraphBaseOperations):

    # the following list is a subset of the annotation_type list in neo4j
    # module
    allowed_motivations = ('tagging', 'describing',
                           'commenting', 'replying', 'segmentation')

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, anno_id=None):
        """ Get an annotation if its id is passed as an argument. """
        self.graph = self.get_service_instance('neo4j')

        params = self.get_input()
        anno_type = params.get('type')
        if anno_type is not None:
            anno_type = anno_type.upper()

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
        elif anno_type is not None:
            annotations = self.graph.Annotation.nodes.filter(
                annotation_type=anno_type)
        else:
            annotations = self.graph.Annotation.nodes.all()

        data = []
        for a in annotations:
            anno = self.get_annotation_response(a)
            data.append(anno)

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):
        """ Create a new annotation. """
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
        if 'motivation' not in data:
            raise RestApiException(
                'Motivation is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)
        motivation = data['motivation']
        if motivation not in self.__class__.allowed_motivations:
            raise RestApiException(
                "Bad motivation parameter: expected one of %s" %
                (self.__class__.allowed_motivations, ),
                status_code=hcodes.HTTP_BAD_REQUEST)
        # check for private and embargo date
        is_private = True if (
            'private' in data and data['private'] is True) else False
        embargo_date = None
        if data.get('embargo') is not None:
            try:
                embargo_date = datetime.datetime.strptime(
                    data['embargo'], '%Y-%m-%d').date()
            except ValueError:
                raise RestApiException('Incorrect embargo date format, should be YYYY-MM-DD',
                                       status_code=hcodes.HTTP_BAD_REQUEST)
        if embargo_date is not None and not is_private:
            raise RestApiException('Embargo date is not allowed for public annotations. '
                                   'Explicitly set the \'private\' parameter to true',
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

        self.graph = self.get_service_instance('neo4j')

        # check user
        user = self.get_current_user()
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

        # check bodies
        bodies = data['body']
        if not isinstance(bodies, list):
            bodies = [bodies]
        for body in bodies:
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
                if 'value' not in body:  # or 'language' not in body:
                    raise RestApiException(
                        'Invalid TextualBody',
                        status_code=hcodes.HTTP_BAD_REQUEST)
            elif b_type == 'TVSBody':
                segments = body.get('segments')
                if segments is None or type(segments) is not list or len(segments) == 0:
                    raise RestApiException(
                        'Invalid TVSBody: invalid or missing segments',
                        status_code=hcodes.HTTP_BAD_REQUEST)
                for s_val in segments:
                    if s_val is None or not SELECTOR_PATTERN.match(s_val):
                        raise RestApiException(
                            'Invalid selector value for: ' + s_val,
                            status_code=hcodes.HTTP_BAD_REQUEST)
            else:
                raise RestApiException(
                    'Invalid body type for: {}'.format(b_type))

        # create manual annotation
        repo = AnnotationRepository(self.graph)
        if motivation == 'describing':
            created_anno = repo.create_dsc_annotation(
                user, bodies, targetNode, selector, is_private, embargo_date)
        elif motivation == 'segmentation':
            if b_type != 'TVSBody':
                raise RestApiException(
                    "Invalid body [{b_type}] for segmentation request. "
                    "Expected TVSBody."
                    .format(b_type=b_type),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if target_type != 'item':
                raise RestApiException(
                    "Invalid target. Only item allowed."
                    .format(b_type=b_type),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            try:
                created_anno = repo.create_tvs_manual_annotation(
                    user, bodies, targetNode, is_private, embargo_date)
            except DuplicatedAnnotationError as error:
                raise RestApiException(error.args[0],
                                       status_code=hcodes.HTTP_BAD_CONFLICT)
        else:
            try:
                created_anno = repo.create_tag_annotation(
                    user, bodies, targetNode, selector, is_private, embargo_date)
            except DuplicatedAnnotationError as error:
                raise RestApiException(
                    error.args[0] + " " + '; '.join(error.args[1]),
                    status_code=hcodes.HTTP_BAD_CONFLICT)

        return self.force_response(
            self.get_annotation_response(created_anno), code=hcodes.HTTP_OK_CREATED)

    @decorate.catch_error()
    @catch_graph_exceptions
    def delete(self, anno_id):
        """ Deletes an annotation. """
        if anno_id is None:
            raise RestApiException(
                "Please specify an annotation id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')

        anno = self.graph.Annotation.nodes.get_or_none(uuid=anno_id)
        # anno = self.getNode(self.graph.Annotation, anno_id, field='uuid')
        if anno is None:
            raise RestApiException(
                'Annotation not found',
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()

        logger.debug('current user: {email} - {uuid}'.format(
            email=user.email, uuid=user.uuid))
        iamadmin = self.auth.verify_admin()
        logger.debug('current user is admin? {0}'.format(iamadmin))

        creator = anno.creator.single()
        is_manual = True if creator is not None else False
        if anno.generator is None and creator is None:
            # manual annotation without creator!
            logger.warn('Invalid state: manual annotation [{id}] '
                        'MUST have a creator'
                        .format(id=anno.uuid))
            raise RestApiException(
                'Annotation with no creator',
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        if is_manual and user.uuid != creator.uuid and not iamadmin:
            raise RestApiException(
                'You cannot delete an annotation that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        body_type = None
        bid = None
        # body_ref = self.get_input(single_parameter='body_ref')
        body_ref = request.args.get('body_ref')
        # logger.debug(body_ref)
        if body_ref is not None:
            if not BODY_PATTERN.match(body_ref):
                raise RestApiException(
                    'Invalid Body format: textual:your_term or resource:your_iri',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            body_type, bid = body_ref.split(':', 1)
            logger.debug('[body type]: {0}, [body id]: {1}'.format(
                body_type, bid))

        repo = AnnotationRepository(self.graph)
        try:
            if is_manual:
                repo.delete_manual_annotation(anno, body_type, bid)
            elif anno.annotation_type == 'TAG':
                repo.delete_auto_annotation(anno)
            else:
                raise ValueError(
                    'Cannot delete anno {id}'.format(id=anno.uuid))
        except ReferenceError as error:
            raise RestApiException(
                error.args[0], status_code=hcodes.HTTP_BAD_REQUEST)

        return self.empty_response()

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def put(self, anno_id):
        """
        Update an annotation.

        Updates are allowed only for particular use cases. For example,
        at the moment, only annotations for notes can be updated.
        """
        if anno_id is None:
            raise RestApiException(
                "Please specify an annotation id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')

        anno = self.graph.Annotation.nodes.get_or_none(uuid=anno_id)
        if anno is None:
            raise RestApiException(
                'Annotation not found',
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()

        creator = anno.creator.single()
        if creator is None:
            raise RestApiException(
                'Annotation with no creator',
                status_code=hcodes.HTTP_BAD_NOTFOUND)
        if user.uuid != creator.uuid:
            raise RestApiException(
                'You cannot update an annotation that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        if anno.annotation_type not in ('DSC', 'COM', 'RPL'):
            raise RestApiException(
                'Operation not allowed for annotation {}'
                .format(anno.annotation_type),
                status_code=hcodes.HTTP_BAD_REQUEST)

        data = self.get_input()
        if anno.annotation_type == 'DSC':
            if 'body' not in data:
                raise RestApiException(
                    'Cannot update annotation without body',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if 'private' in data:
                if not isinstance(data['private'], bool):
                    raise RestApiException(
                        'Invalid private',
                        status_code=hcodes.HTTP_BAD_REQUEST)
                anno.private = data['private']
                if not anno.private:
                    # force embargo deletion
                    anno.embargo = None
            if 'embargo' in data and anno.private:
                # ignore incoming embargo for public note
                try:
                    anno.embargo = datetime.datetime.strptime(
                        data['embargo'], '%Y-%m-%d').date()
                except ValueError:
                    raise RestApiException('Incorrect embargo date format,'
                                           ' should be YYYY-MM-DD',
                                           status_code=hcodes.HTTP_BAD_REQUEST)
            # update the body
            body = data['body']
            if isinstance(body, list):
                raise RestApiException(
                    'Expected single body',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            b_type = body.get('type')
            if b_type != 'TextualBody':
                raise RestApiException(
                    'Invalid body type for: {}. Expected TextualBody.'
                    .format(b_type))
            if 'value' not in body:
                raise RestApiException(
                    'Invalid TextualBody',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            # expected single body for DSC annotations
            anno_body = anno.bodies.single()
            textual_body = anno_body.downcast()
            textual_body.value = body['value']
            if 'language' in body:
                textual_body.language = body['language']
            textual_body.save()
            anno.save()
        else:
            raise RestApiException(
                'Not yet implemented',
                status_code=hcodes.HTTP_NOT_IMPLEMENTED)

        updated_anno = self.get_annotation_response(anno)
        del(updated_anno['links'])

        return self.force_response(updated_anno)

    def get_annotation_response(self, anno):
        """
        Utility method to build DTO for annotation model.
        """
        res = self.getJsonResponse(anno, max_relationship_depth=0)
        if anno.creator is not None:
            creator = self.getJsonResponse(
                anno.creator.single(), max_relationship_depth=0)
            if 'links' in creator:
                del(creator['links'])
            res['creator'] = creator
        res['bodies'] = []
        for b in anno.bodies.all():
            anno_body = b.downcast()
            body = self.getJsonResponse(anno_body, max_relationship_depth=0)
            if 'links' in body:
                del(body['links'])
            if anno.annotation_type == 'TVS':
                segments = []
                for segment in anno_body.segments:
                    # look at the most derivative class
                    json_segment = self.getJsonResponse(
                        segment.downcast(), max_relationship_depth=0)
                    if 'links' in json_segment:
                        del(json_segment['links'])
                    segments.append(json_segment)
                body['segments'] = segments
            res['bodies'].append(body)
        res['targets'] = []
        for t in anno.targets.all():
            target = self.getJsonResponse(
                t.downcast(), max_relationship_depth=0)
            if 'links' in target:
                del(target['links'])
            res['targets'].append(target)
        source = self.getJsonResponse(
            anno.source_item.single(), max_relationship_depth=0)
        if 'links' in source:
            del(source['links'])
        res['source'] = source
        return res
