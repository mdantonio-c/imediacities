from pathlib import Path
from typing import Optional

from imc.endpoints import IMCEndpoint
from imc.security import authz
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.tasks.services.creation_repository import CreationRepository
from restapi import decorators
from restapi.config import get_backend_url
from restapi.connectors import celery, neo4j
from restapi.exceptions import BadRequest, Conflict, Forbidden, NotFound
from restapi.models import fields, validate
from restapi.rest.definition import Response
from restapi.services.authentication import Role, User
from restapi.services.download import Downloader
from restapi.utilities.logs import log


class Models(IMCEndpoint):
    @decorators.endpoint(
        path="/models/<model_id>",
        summary="Get 3D-model metadata",
        description="Returns the requested 3D-model",
        responses={
            200: "3D-model successfully retrieved",
            404: "The 3D-model does not exist.",
        },
    )
    def get(self, model_id: str) -> Response:
        """Get the NonAVEntity 3D-model passed as argument."""
        log.debug("getting NonAVEntity 3d-model id: {}", model_id)
        graph = neo4j.get_instance()

        try:
            v = graph.NonAVEntity.nodes.get(uuid=model_id, non_av_type="3d-model")
        except graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity 3d-model with UUID {} does not exist", model_id)
            raise NotFound("Please specify a valid 3d-model id")

        model = self.getJsonResponse(
            v,
            max_relationship_depth=1,
            relationships_expansion=[
                "record_sources.provider",
                "item.ownership",
                "item.three_dim_format",
            ],
        )
        item = v.item.single()
        api_url = get_backend_url()
        model_url = f"{api_url}/api/models/{v.uuid}/content?type=3d-model"
        model["links"] = {}
        model["links"]["content"] = model_url
        if item.thumbnail is not None:
            thumbnail_url = f"{api_url}/api/models/{v.uuid}/content?type=thumbnail"
            model["links"]["thumbnail"] = thumbnail_url

        return self.response(model)

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.database_transaction
    @decorators.endpoint(
        path="/models/<model_id>",
        summary="Delete a 3d-model description",
        responses={200: "3d-model successfully deleted"},
    )
    def delete(self, model_id: str, user: User) -> Response:
        """Delete existing 3d-model description."""
        log.debug("deleting NonAVEntity 3d-model UUID: {}", model_id)
        graph = neo4j.get_instance()

        if model_id is None:
            raise BadRequest("Please specify a valid 3d-model id")

        try:
            v = graph.NonAVEntity.nodes.get(uuid=model_id, non_av_type="3d-model")
            repo = CreationRepository(graph)
            repo.delete_non_av_entity(v)
            return self.empty_response()
        except graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity 3d-model with UUID {} does not exist", model_id)
            raise NotFound("Please specify a valid 3d-model id")


class ModelItem(IMCEndpoint):
    @decorators.auth.require_any(Role.ADMIN, "Archive")
    @decorators.database_transaction
    @decorators.use_kwargs(
        {
            "public_access": fields.Bool(
                required=True,
                metadata={
                    "description": "Whether or not the item is accessible by a public user."
                },
            )
        }
    )
    @decorators.endpoint(
        path="/models/<model_id>/item",
        summary="Update public access flag for the given 3d-model",
        responses={
            204: "Item info successfully updated.",
            400: "Request not valid.",
            403: "Operation forbidden.",
            404: "3d-model does not exist.",
        },
    )
    def put(self, model_id: str, public_access: bool, user: User) -> Response:
        """Allow user to update item information."""
        log.debug("Update Item for NonAVEntity 3d-model UUID: {}", model_id)
        graph = neo4j.get_instance()

        if not (
            model := graph.NonAVEntity.nodes.get_or_none(
                uuid=model_id, non_av_type="3d-model"
            )
        ):
            log.debug("NonAVEntity 3d-model with UUID {} does not exist", model_id)
            raise NotFound("Please specify a valid 3d-model id")

        if not (item := model.item.single()):
            raise NotFound(
                "NonAVEntity 3d-model not correctly imported: item info not found"
            )

        repo = CreationRepository(graph)
        if not repo.item_belongs_to_user(item, user):
            log.error("User {} not allowed to edit 3d-model {}", user.email, model_id)
            raise Forbidden(
                "Cannot update public access for 3d-models that does not belong to you"
            )

        item.public_access = public_access
        item.save()
        log.debug(
            "Item successfully updated for NonAVEntity 3d-model UUID {}. {}",
            model_id,
            item,
        )

        return self.empty_response()


class ModelAnnotations(IMCEndpoint):
    """Get all annotations for a given 3d-model."""

    @decorators.use_kwargs(
        {
            "anno_type": fields.Str(
                required=False,
                data_key="type",
                metadata={
                    "description": "Filter by annotation type (e.g. TAG, DSC, LNK)"
                },
                validate=validate.OneOf(["TAG", "DSC", "LNK"]),
            )
        },
        location="query",
    )
    @decorators.endpoint(
        path="/models/<model_id>/annotations",
        summary="Gets 3d-model annotations",
        description="Returns all the annotations targeting the given 3d-model item.",
        responses={200: "An annotation object", 404: "3d-model does not exist"},
    )
    def get(self, model_id: str, anno_type: Optional[str] = None) -> Response:
        log.debug("get annotations for NonAVEntity 3d-model UUID: {}", model_id)
        graph = neo4j.get_instance()
        data = []

        model = graph.NonAVEntity.nodes.get_or_none(
            uuid=model_id, non_av_type="3d-model"
        )
        if not model:
            log.debug("NonAVEntity 3d-model with UUID {} does not exist", model_id)
            raise NotFound("Please specify a valid 3d-model id")

        # ?????????????????????
        # This endpoint does not have any authentication
        user = self.get_user()

        item = model.item.single()
        for anno in item.targeting_annotations:
            if anno_type is not None and anno.annotation_type != anno_type:
                continue
            if anno.private:
                if anno.creator is None:
                    # expected ALWAYS a creator for private annotation
                    log.warning(
                        "Invalid state: missing creator for private " "anno [UUID:{}]",
                        anno.uuid,
                    )
                    continue
                creator = anno.creator.single()
                if user is None or creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(anno, max_relationship_depth=0)
            if (
                anno.annotation_type in ("TAG", "DSC", "LNK")
                and anno.creator is not None
            ):
                res["creator"] = self.getJsonResponse(
                    anno.creator.single(), max_relationship_depth=0
                )
            # attach bodies
            res["bodies"] = []
            for b in anno.bodies.all():
                mdb = b.downcast()
                if anno.annotation_type == "TAG" and "ODBody" in mdb.labels():
                    # object detection body
                    body = self.getJsonResponse(
                        mdb.object_type.single(), max_relationship_depth=0
                    )
                else:
                    body = self.getJsonResponse(mdb, max_relationship_depth=0)
                res["bodies"].append(body)
            data.append(res)

        return self.response(data)


class ModelContent(IMCEndpoint):
    """Gets 3d-model content or thumbnail"""

    @decorators.auth.optional()
    @decorators.use_kwargs(
        {
            "content_type": fields.Str(
                required=True,
                data_key="type",
                metadata={"description": "content type (e.g. 3d-model, thumbnail)"},
                validate=validate.OneOf(["3d-model", "thumbnail"]),
            ),
            "thumbnail_size": fields.Str(
                required=False,
                data_key="size",
                metadata={"description": "used to get large thumbnails"},
                validate=validate.OneOf(["large"]),
            ),
        },
        location="query",
    )
    @decorators.preload(callback=authz.check_permissions)
    @decorators.endpoint(
        path="/models/<model_id>/content",
        summary="Gets the 3d-model content",
        responses={
            200: "3d-model content successfully retrieved",
            404: "The 3d-model content does not exists",
        },
    )
    def get(
        self,
        model_id: str,
        content_type: str,
        user: Optional[User],
        thumbnail_size: Optional[str] = None,
    ) -> Response:
        log.info("get 3d-model content for id {}", model_id)

        graph = neo4j.get_instance()
        model = None
        try:
            model = graph.NonAVEntity.nodes.get(uuid=model_id, non_av_type="3d-model")
        except graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity 3d-model with UUID {} does not exist", model_id)
            raise NotFound("Please specify a valid 3d-model id")

        item = model.item.single()
        log.debug("item data: " + format(item))
        if content_type == "3d-model":
            # TODO manage here content access (see issue 190)
            # always return the other version if available
            model_uri = item.uri
            other_version = item.other_version.single()
            if other_version is not None:
                model_uri = other_version.uri
            log.debug("3d-model content uri: {}", model_uri)
            if model_uri is None:
                raise NotFound("3d-model not found")

            model_path = Path(model_uri)

            return Downloader.send_file_content(
                filename=model_path.name,
                subfolder=model_path.parent,
                # 3d-model is always glb
                mime="model/gltf-binary",
                # mime="application/octet-stream",
            )

        if content_type == "thumbnail":
            thumbnail_uri = item.thumbnail
            log.debug("thumbnail content uri: {}", thumbnail_uri)
            # if thumbnail_size and thumbnail_size== "large":
            # large is the only allowed size at the moment
            if thumbnail_size:
                # load large image file as the original (i.e. transcoded.jpg)
                thumbnail_uri = item.uri
                log.debug("request for large thumbnail: {}", thumbnail_uri)
            if thumbnail_uri is None:
                raise NotFound("Thumbnail not found")

            thumbnail_path = Path(thumbnail_uri)
            return Downloader.send_file_content(
                filename=thumbnail_path.name,
                subfolder=thumbnail_path.parent,
                # thumbnail is always jpeg
                mime="image/jpeg",
            )

        # it should never be reached
        raise BadRequest(
            f"Invalid content type: {content_type}",
        )
