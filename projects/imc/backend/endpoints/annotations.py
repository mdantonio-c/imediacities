"""
Handle annotations
"""

import datetime
import re

from imc.endpoints import IMCEndpoint
from imc.models import PatchDocument
from imc.tasks.services.annotation_repository import (
    AnnotationRepository,
    DuplicatedAnnotationError,
)
from restapi import decorators
from restapi.exceptions import (
    BadRequest,
    Conflict,
    Forbidden,
    NotFound,
    RestApiException,
)
from restapi.models import fields
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log

TARGET_PATTERN = re.compile("(item|shot|anno):([a-z0-9-])+")
BODY_PATTERN = re.compile("(resource|textual):.+")
SELECTOR_PATTERN = re.compile(r"t=\d+,\d+")

__author__ = "Giuseppe Trotta(g.trotta@cineca.it)"


#####################################
class Annotations(IMCEndpoint):

    # the following list is a subset of the annotation_type list in neo4j
    # module
    allowed_motivations = (
        "tagging",
        "describing",
        "linking",
        "commenting",
        "replying",
        "segmentation",
    )

    labels = ["annotation"]
    _GET = {
        "/annotations": {
            "summary": "Get a single annotation",
            "description": "Returns a single annotation for its uuid",
            "responses": {
                "200": {
                    "description": "An annotation",
                    "schema": {"$ref": "#/definitions/Annotation"},
                },
                "404": {"description": "Annotation does not exist."},
            },
        },
        "/annotations/<anno_id>": {
            "summary": "Get a single annotation",
            "description": "Returns a single annotation for its uuid",
            "responses": {
                "200": {
                    "description": "An annotation",
                    "schema": {"$ref": "#/definitions/Annotation"},
                },
                "404": {"description": "Annotation does not exist."},
            },
        },
    }
    _POST = {
        "/annotations": {
            "summary": "Create an annotation",
            "description": "Add a new annotation using WADM-based model to some specified target",
            "parameters": [
                {
                    "name": "annotation",
                    "in": "body",
                    "description": "The annotation to create.",
                    "schema": {"$ref": "#/definitions/Annotation"},
                }
            ],
            "responses": {
                "201": {"description": "Annotation successfully created."},
                "400": {"description": "Annotation couldn't have been created."},
            },
        }
    }
    _PUT = {
        "/annotations/<anno_id>": {
            "summary": "Updates an annotation",
            "description": "Update a single annotation identified via its uuid",
            "parameters": [
                {
                    "name": "annotation",
                    "in": "body",
                    "required": True,
                    "description": "The annotation to update.",
                    "schema": {"$ref": "#/definitions/Annotation"},
                }
            ],
            "responses": {
                "204": {"description": "Annotation successfully updated."},
                "400": {
                    "description": "Annotation cannot be updated. Operation allowed only for specific use cases."
                },
                "403": {"description": "Operation forbidden."},
                "404": {"description": "Annotation does not exist."},
            },
        }
    }
    _PATCH = {
        "/annotations/<anno_id>": {
            "summary": "Updates partially an annotation",
            "description": "Update partially a single annotation identified via its uuid. At the moment, used to update segment list in a segmentation annotation.",
            "responses": {
                "204": {"description": "Annotation successfully updated."},
                "400": {
                    "description": "Annotation cannot be updated. Operation allowed only for specific use cases."
                },
                "403": {"description": "Operation forbidden."},
                "404": {"description": "Annotation does not exist."},
            },
        }
    }
    _DELETE = {
        "/annotations/<anno_id>": {
            "summary": "Deletes an annotation",
            "description": "Delete a single annotation identified via its uuid",
            "responses": {
                "204": {"description": "Annotation successfully deleted."},
                "400": {
                    "description": "Annotation cannot be deleted. No body found for the given reference."
                },
                "403": {"description": "Operation forbidden."},
                "404": {"description": "Annotation does not exist."},
            },
        }
    }

    @decorators.auth.require()
    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {
            "anno_type": fields.Str(
                required=False,
                data_key="type",
                description="filter by annotation type",
            )
        },
        location="query",
    )
    def get(self, anno_id=None, anno_type=None):
        """ Get an annotation if its id is passed as an argument. """
        self.graph = self.get_service_instance("neo4j")

        if anno_id is None and not self.verify_admin():
            raise RestApiException(
                "You are not authorized: missing privileges",
                status_code=hcodes.HTTP_BAD_UNAUTHORIZED,
            )

        if anno_id:
            # check if the video exists
            anno = self.graph.Annotation.nodes.get_or_none(uuid=anno_id)
            if not anno:
                log.debug("Annotation with uuid {} does not exist", anno_id)
                raise RestApiException(
                    "Please specify a valid annotation id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND,
                )
            annotations = [anno]
        elif anno_type:
            annotations = self.graph.Annotation.nodes.filter(annotation_type=anno_type)
        else:
            annotations = self.graph.Annotation.nodes.all()

        data = []
        for a in annotations:
            anno = self.get_annotation_response(a)
            data.append(anno)

        return self.response(data)

    @decorators.auth.require()
    @decorators.catch_graph_exceptions
    @decorators.graph_transactions
    def post(self):
        """ Create a new annotation. """
        # TODO access control (annotation cannot be created by general user if not in public domain)
        data = self.get_input()
        if len(data) == 0:
            raise RestApiException("Empty input", status_code=hcodes.HTTP_BAD_REQUEST)
        if "target" not in data:
            raise RestApiException(
                "Target is mandatory", status_code=hcodes.HTTP_BAD_REQUEST
            )
        if "body" not in data:
            raise RestApiException(
                "Body is mandatory", status_code=hcodes.HTTP_BAD_REQUEST
            )
        if "motivation" not in data:
            raise RestApiException(
                "Motivation is mandatory", status_code=hcodes.HTTP_BAD_REQUEST
            )
        motivation = data["motivation"]
        if motivation not in self.__class__.allowed_motivations:
            raise RestApiException(
                "Bad motivation parameter: expected one of {}".format(
                    self.__class__.allowed_motivations
                ),
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        # check for private and embargo date
        is_private = True if ("private" in data and data["private"] is True) else False
        embargo_date = None
        if data.get("embargo") is not None:
            try:
                embargo_date = datetime.datetime.strptime(
                    data["embargo"], "%Y-%m-%d"
                ).date()
            except ValueError:
                raise RestApiException(
                    "Incorrect embargo date format, should be YYYY-MM-DD",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
        if embargo_date is not None and not is_private:
            raise RestApiException(
                "Embargo date is not allowed for public annotations. "
                "Explicitly set the 'private' parameter to true",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        # check the target
        target = data["target"]
        log.debug("Annotate target: {}", target)
        if not TARGET_PATTERN.match(target):
            raise RestApiException(
                "Invalid Target format", status_code=hcodes.HTTP_BAD_REQUEST
            )
        target_type, tid = target.split(":")
        log.debug("target type: {}, target id: {}", target_type, tid)

        self.graph = self.get_service_instance("neo4j")

        # check user
        user = self.get_user()
        if user is None:
            raise RestApiException("Invalid user", status_code=hcodes.HTTP_BAD_REQUEST)

        targetNode = None
        if target_type == "item":
            targetNode = self.graph.Item.nodes.get_or_none(uuid=tid)
        elif target_type == "shot":
            targetNode = self.graph.Shot.nodes.get_or_none(uuid=tid)
        elif target_type == "anno":
            targetNode = self.graph.Annotation.nodes.get_or_none(uuid=tid)
        else:
            # this should never be reached
            raise RestApiException(
                "Invalid target type", status_code=hcodes.HTTP_SERVER_ERROR
            )

        if targetNode is None:
            raise RestApiException(
                "Target [" + target_type + "][" + tid + "] does not exist",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        # check the selector
        selector = data.get("selector", None)
        log.debug("selector: {}", selector)
        if selector is not None:
            if selector["type"] != "FragmentSelector":
                raise RestApiException(
                    "Invalid selector type for: {}".format(selector["type"]),
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            s_val = selector["value"]
            if s_val is None or not SELECTOR_PATTERN.match(s_val):
                raise RestApiException(
                    "Invalid selector value for: " + s_val,
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )

        # check bodies
        bodies = data["body"]
        if not isinstance(bodies, list):
            bodies = [bodies]
        for body in bodies:
            b_type = body.get("type")
            if b_type == "ResourceBody":
                source = body.get("source")
                if source is None:
                    raise RestApiException(
                        "Missing Source in the ResourceBody",
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
                # here we expect the source as an IRI or a structured object
                # 1) just the IRI
                if isinstance(source, str):
                    pass
                # 2) structured object
                elif "iri" not in source or "name" not in source:
                    raise RestApiException(
                        "Invalid ResourceBody", status_code=hcodes.HTTP_BAD_REQUEST
                    )
            elif b_type == "TextualBody":
                if "value" not in body:  # or 'language' not in body:
                    raise RestApiException(
                        "Invalid TextualBody", status_code=hcodes.HTTP_BAD_REQUEST
                    )
            elif b_type == "TVSBody":
                segments = body.get("segments")
                if segments is None or type(segments) is not list or len(segments) == 0:
                    raise RestApiException(
                        "Invalid TVSBody: invalid or missing segments",
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
                for s_val in segments:
                    if s_val is None or not SELECTOR_PATTERN.match(s_val):
                        raise RestApiException(
                            "Invalid selector value for: " + s_val,
                            status_code=hcodes.HTTP_BAD_REQUEST,
                        )
            elif b_type == "BibliographicReference":
                # validate reference body
                if "value" not in body:
                    raise RestApiException(
                        "Invalid BibliographicReference",
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
                value = body.get("value")
                if "title" not in value:
                    raise RestApiException(
                        "Invalid BibliographicReference: missing title",
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
                authors = value.get("authors")
                if authors is None or len(authors) == 0:
                    raise RestApiException(
                        "Invalid BibliographicReference: missing authors",
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
            else:
                raise RestApiException(f"Invalid body type for: {b_type}")

        # create manual annotation
        repo = AnnotationRepository(self.graph)
        if motivation == "describing":
            created_anno = repo.create_dsc_annotation(
                user, bodies, targetNode, selector, is_private, embargo_date
            )
        elif motivation == "segmentation":
            if b_type != "TVSBody":
                raise RestApiException(
                    f"Invalid body [{b_type}] for segmentation request. "
                    "Expected TVSBody.",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            if target_type != "item":
                raise RestApiException(
                    "Invalid target. Only item allowed.",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            try:
                created_anno = repo.create_tvs_manual_annotation(
                    user, bodies, targetNode, is_private, embargo_date
                )
            except DuplicatedAnnotationError as error:
                raise RestApiException(
                    error.args[0], status_code=hcodes.HTTP_BAD_CONFLICT
                )
        elif motivation == "linking":
            try:
                created_anno = repo.create_link_annotation(
                    user, bodies, targetNode, is_private, embargo_date
                )
            except DuplicatedAnnotationError as error:
                raise RestApiException(
                    error.args[0], status_code=hcodes.HTTP_BAD_CONFLICT
                )
        else:
            try:
                created_anno = repo.create_tag_annotation(
                    user, bodies, targetNode, selector, is_private, embargo_date
                )
            except DuplicatedAnnotationError as error:
                raise RestApiException(
                    error.args[0] + " " + "; ".join(error.args[1]),
                    status_code=hcodes.HTTP_BAD_CONFLICT,
                )

        return self.response(
            self.get_annotation_response(created_anno), code=hcodes.HTTP_OK_CREATED
        )

    @decorators.auth.require()
    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {
            "body_ref": fields.Str(
                required=False,
                description="optional body reference for annotation with multiple bodies. This reference MUST be in the form 'textual:your_term_value' or 'resource:your_term_IRI'",
            )
        },
        location="query",
    )
    def delete(self, anno_id, body_ref=None):
        """ Deletes an annotation. """

        self.graph = self.get_service_instance("neo4j")

        anno = self.graph.Annotation.nodes.get_or_none(uuid=anno_id)
        if anno is None:
            raise RestApiException(
                "Annotation not found", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_user()

        log.debug("current user: {email} - {uuid}", email=user.email, uuid=user.uuid)
        iamadmin = self.verify_admin()
        log.debug("current user is admin? {0}", iamadmin)

        creator = anno.creator.single()
        is_manual = True if creator is not None else False
        if anno.generator is None and creator is None:
            # manual annotation without creator!
            log.warning(
                "Invalid state: manual annotation [{id}] MUST have a creator",
                id=anno.uuid,
            )
            raise RestApiException(
                "Annotation with no creator", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        if is_manual and user.uuid != creator.uuid and not iamadmin:
            raise RestApiException(
                "You cannot delete an annotation that does not belong to you",
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        body_type = None
        bid = None
        if body_ref:
            if not BODY_PATTERN.match(body_ref):
                raise RestApiException(
                    "Invalid Body format: textual:your_term or resource:your_iri",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            body_type, bid = body_ref.split(":", 1)
            log.debug("[body type]: {0}, [body id]: {1}", body_type, bid)

        repo = AnnotationRepository(self.graph)
        try:
            if is_manual and anno.annotation_type != "TVS":
                repo.delete_manual_annotation(anno, body_type, bid)
            elif is_manual and anno.annotation_type == "TVS":
                repo.delete_tvs_manual_annotation(anno)
            elif anno.annotation_type == "TAG":
                repo.delete_auto_annotation(anno)
            else:
                raise ValueError(f"Cannot delete anno {anno.uuid}")
        except ReferenceError as error:
            raise RestApiException(error.args[0], status_code=hcodes.HTTP_BAD_REQUEST)

        return self.empty_response()

    @decorators.auth.require()
    @decorators.catch_graph_exceptions
    @decorators.graph_transactions
    def put(self, anno_id):
        """
        Update an annotation.

        Updates are allowed only for particular use cases. For example,
        at the moment, only annotations for notes can be updated.
        """
        if anno_id is None:
            raise RestApiException(
                "Please specify an annotation id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance("neo4j")

        anno = self.graph.Annotation.nodes.get_or_none(uuid=anno_id)
        if anno is None:
            raise RestApiException(
                "Annotation not found", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_user()

        creator = anno.creator.single()
        if creator is None:
            raise RestApiException(
                "Annotation with no creator", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        if user.uuid != creator.uuid:
            raise RestApiException(
                "You cannot update an annotation that does not belong to you",
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        if anno.annotation_type not in ("DSC", "COM", "RPL"):
            raise RestApiException(
                f"Operation not allowed for annotation {anno.annotation_type}",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        data = self.get_input()
        if anno.annotation_type == "DSC":
            if "body" not in data:
                raise RestApiException(
                    "Cannot update annotation without body",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            if "private" in data:
                if not isinstance(data["private"], bool):
                    raise RestApiException(
                        "Invalid private", status_code=hcodes.HTTP_BAD_REQUEST
                    )
                anno.private = data["private"]
                if not anno.private:
                    # force embargo deletion
                    anno.embargo = None
            if "embargo" in data and anno.private:
                # ignore incoming embargo for public note
                try:
                    anno.embargo = datetime.datetime.strptime(
                        data["embargo"], "%Y-%m-%d"
                    ).date()
                except ValueError:
                    raise RestApiException(
                        "Incorrect embargo date format," " should be YYYY-MM-DD",
                        status_code=hcodes.HTTP_BAD_REQUEST,
                    )
            # update the body
            body = data["body"]
            if isinstance(body, list):
                raise RestApiException(
                    "Expected single body", status_code=hcodes.HTTP_BAD_REQUEST
                )
            b_type = body.get("type")
            if b_type != "TextualBody":
                raise RestApiException(
                    f"Invalid body type for: {b_type}. Expected TextualBody."
                )
            if "value" not in body:
                raise RestApiException(
                    "Invalid TextualBody", status_code=hcodes.HTTP_BAD_REQUEST
                )
            # expected single body for DSC annotations
            anno_body = anno.bodies.single()
            textual_body = anno_body.downcast()
            textual_body.value = body["value"]
            if "language" in body:
                textual_body.language = body["language"]
            textual_body.save()
            anno.save()
        else:
            raise RestApiException(
                "Not yet implemented", status_code=hcodes.HTTP_NOT_IMPLEMENTED
            )

        updated_anno = self.get_annotation_response(anno)

        return self.response(updated_anno)

    @decorators.auth.require()
    @decorators.catch_graph_exceptions
    @decorators.graph_transactions
    @decorators.use_kwargs(PatchDocument)
    def patch(self, anno_id, patch_op, path, value):

        self.graph = self.get_service_instance("neo4j")

        anno = self.graph.Annotation.nodes.get_or_none(uuid=anno_id)
        if anno is None:
            raise NotFound("Annotation not found")

        if not (creator := anno.creator.single()):
            raise NotFound("Annotation with no creator")

        user = self.get_user()
        if user.uuid != creator.uuid:
            raise Forbidden(
                "You cannot update an annotation that does not belong to you",
            )

        if anno.annotation_type != "TVS":
            raise BadRequest(
                f"Operation not allowed for annotation {anno.annotation_type}"
            )

        repo = AnnotationRepository(self.graph)

        if patch_op == "remove":
            log.debug("remove a segment with uuid:{uuid}", uuid=value)
            segment = self.graph.VideoSegment.nodes.get_or_none(uuid=value)

            if not segment:
                raise NotFound(f"Segment with ID {value} not found.")

            try:
                repo.remove_segment(anno, segment)
            except ValueError as error:
                raise BadRequest(error.args[0])
            except DuplicatedAnnotationError as error:
                raise Conflict(error.args[0])

            return self.empty_response()

        if patch_op == "add":
            log.debug("add a segment with value:{val}", val=value)
            if not SELECTOR_PATTERN.match(value):
                raise BadRequest(f"Invalid value for: {value}")

            try:
                repo.add_segment(anno, value)
            except DuplicatedAnnotationError as error:
                raise Conflict(error.args[0])

            updated_anno = self.get_annotation_response(anno)

            return self.response(updated_anno)

    def get_annotation_response(self, anno):
        """
        Utility method to build DTO for annotation model.
        """
        res = self.getJsonResponse(anno, max_relationship_depth=0)
        if anno.creator is not None:
            res["creator"] = self.getJsonResponse(
                anno.creator.single(), max_relationship_depth=0
            )

        res["bodies"] = []
        for b in anno.bodies.all():
            anno_body = b.downcast()
            body = self.getJsonResponse(anno_body, max_relationship_depth=0)
            if anno.annotation_type == "TVS":
                segments = []
                for segment in anno_body.segments:
                    # look at the most derivative class
                    json_segment = self.getJsonResponse(
                        segment.downcast(), max_relationship_depth=0
                    )
                    segments.append(json_segment)
                body["segments"] = segments
            res["bodies"].append(body)

        res["targets"] = []
        for t in anno.targets.all():
            target = self.getJsonResponse(t.downcast(), max_relationship_depth=0)
            res["targets"].append(target)

        res["source"] = self.getJsonResponse(
            anno.source_item.single(), max_relationship_depth=0
        )
        return res