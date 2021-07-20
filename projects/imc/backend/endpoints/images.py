"""
Handle your image entity
"""
import os

from flask import send_file
from imc.endpoints import IMCEndpoint
from imc.security import authz
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.tasks.services.creation_repository import CreationRepository
from restapi import decorators
from restapi.config import get_backend_url
from restapi.connectors import celery, neo4j
from restapi.exceptions import BadRequest, Conflict, Forbidden, NotFound, ServerError
from restapi.models import fields, validate
from restapi.services.authentication import Role
from restapi.services.download import Downloader
from restapi.utilities.logs import log


class Images(IMCEndpoint):

    labels = ["image"]

    @decorators.endpoint(
        path="/images/<image_id>",
        summary="Get image metadata",
        description="Returns the requested image",
        responses={
            200: "Image successfully retrieved",
            404: "The image does not exist.",
        },
    )
    def get(self, image_id):
        """Get the NonAVEntity passed as argument."""
        log.debug("getting NonAVEntity id: {}", image_id)
        self.graph = neo4j.get_instance()

        try:
            v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise NotFound("Please specify a valid image id")

        image = self.getJsonResponse(
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
        image_url = f"{api_url}/api/images/{v.uuid}/content?type=image"
        image["links"] = {}
        image["links"]["content"] = image_url
        if item.thumbnail is not None:
            thumbnail_url = f"{api_url}/api/images/{v.uuid}/content?type=thumbnail"
            image["links"]["thumbnail"] = thumbnail_url
        summary_url = f"{api_url}/api/images/{v.uuid}/content?type=summary"
        image["links"]["summary"] = summary_url

        return self.response(image)

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.database_transaction
    @decorators.endpoint(
        path="/images/<image_id>",
        summary="Delete a image description",
        responses={200: "Image successfully deleted"},
    )
    def delete(self, image_id):
        """Delete existing image description."""
        log.debug("deliting NonAVEntity id: {}", image_id)
        self.graph = neo4j.get_instance()

        if image_id is None:
            raise BadRequest("Please specify a valid image id")

        try:
            v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
            repo = CreationRepository(self.graph)
            repo.delete_non_av_entity(v)
            return self.empty_response()
        except self.graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise NotFound("Please specify a valid image id")


class ImageItem(IMCEndpoint):
    @decorators.auth.require_any(Role.ADMIN, "Archive")
    @decorators.database_transaction
    @decorators.use_kwargs(
        {
            "public_access": fields.Bool(
                required=True,
                description="Whether or not the item is accessible by a public user.",
            )
        }
    )
    @decorators.endpoint(
        path="/images/<image_id>/item",
        summary="Update public access flag for the given image",
        responses={
            204: "Item info successfully updated.",
            400: "Request not valid.",
            403: "Operation forbidden.",
            404: "Image does not exist.",
        },
    )
    def put(self, image_id, public_access):
        """Allow user to update item information."""
        log.debug("Update Item for NonAVEntity uuid: {}", image_id)

        self.graph = neo4j.get_instance()

        if not (image := self.graph.NonAVEntity.nodes.get_or_none(uuid=image_id)):
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise NotFound("Please specify a valid image id")

        if not (item := image.item.single()):
            raise NotFound("NonAVEntity not correctly imported: item info not found")

        user = self.get_user()

        # Can't happen since auth is required
        if not user:  # pragma: no cover
            raise ServerError("User misconfiguration")

        repo = CreationRepository(self.graph)
        if not repo.item_belongs_to_user(item, user):
            log.error("User {} not allowed to edit image {}", user.email, image_id)
            raise Forbidden(
                "Cannot update public access for images that does not belong to you"
            )

        item.public_access = public_access
        item.save()
        log.debug(
            "Item successfully updated for NonAVEntity uuid {}. {}", image_id, item
        )

        return self.empty_response()


class ImageAnnotations(IMCEndpoint):
    """Get all image annotations for a given image."""

    labels = ["image_annotations"]

    @decorators.use_kwargs(
        {
            "anno_type": fields.Str(
                required=False,
                data_key="type",
                description="Filter by annotation type (e.g. TAG, DSC)",
                validate=validate.OneOf(["TAG", "DSC"]),
            )
        },
        location="query",
    )
    @decorators.endpoint(
        path="/images/<image_id>/annotations",
        summary="Gets image annotations",
        description="Returns all the annotations targeting the given image item.",
        responses={200: "An annotation object", 404: "Image does not exist"},
    )
    def get(self, image_id, anno_type=None):
        log.debug("get annotations for NonAVEntity id: {}", image_id)

        self.graph = neo4j.get_instance()
        data = []

        image = self.graph.NonAVEntity.nodes.get_or_none(uuid=image_id)
        if not image:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise NotFound("Please specify a valid image id")

        user = self.get_user()

        item = image.item.single()
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


class ImageContent(IMCEndpoint, Downloader):
    """Gets image content or thumbnail"""

    labels = ["image"]

    @decorators.auth.optional()
    @decorators.use_kwargs(
        {
            "content_type": fields.Str(
                required=True,
                data_key="type",
                description="content type (e.g. image, thumbnail)",
                validate=validate.OneOf(["image", "thumbnail"]),
            ),
            "thumbnail_size": fields.Str(
                required=False,
                data_key="size",
                description="used to get large thumbnails",
                validate=validate.OneOf(["large"]),
            ),
        },
        location="query",
    )
    @decorators.endpoint(
        path="/images/<image_id>/content",
        summary="Gets the image content",
        responses={
            200: "Image content successfully retrieved",
            404: "The image content does not exists",
        },
    )
    @authz.pre_authorize
    def get(self, image_id, content_type, thumbnail_size=None):
        log.info("get image content for id {}", image_id)

        self.graph = neo4j.get_instance()
        image = None
        try:
            image = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise NotFound("Please specify a valid image id")

        item = image.item.single()
        log.debug("item data: " + format(item))
        if content_type in ["image", "3d-model"]:
            # TODO manage here content access (see issue 190)
            # always return the other version if available
            image_uri = item.uri
            other_version = item.other_version.single()
            if other_version is not None:
                image_uri = other_version.uri
            log.debug("image content uri: {}", image_uri)
            if image_uri is None:
                raise NotFound("Image not found")
            filename = os.path.basename(image_uri)
            folder = os.path.dirname(image_uri)

            # image is always jpeg

            # return self.send_file_partial(image_uri, mime)
            return self.download(filename=filename, subfolder=folder, mime="image/jpeg")

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
            return send_file(thumbnail_uri, mimetype="image/jpeg")

        # it should never be reached
        raise BadRequest(
            f"Invalid content type: {content_type}",
        )


class ImageTools(IMCEndpoint):

    labels = ["image_tools"]

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.use_kwargs(
        {
            "tool": fields.String(
                required=True,
                description="Tool to be launched.",
                validate=validate.OneOf(["object-detection", "building-recognition"]),
            ),
            "operation": fields.String(
                required=False,
                description="At the moment used only to delete automatic tags.",
                validate=validate.OneOf(["delete"]),
            ),
        }
    )
    @decorators.endpoint(
        path="/images/<image_id>/tools",
        summary="Allow to launch the execution of some image tools.",
        responses={
            202: "Execution task accepted.",
            200: "Execution completed successfully. only with delete operation.",
            403: "Request forbidden.",
            404: "Image not found.",
            409: "Invalid state e.g. object detection results cannot be imported twice",
        },
    )
    def post(self, image_id, tool, operation=None):

        log.debug("launch automatic tool for image id: {}", image_id)

        self.graph = neo4j.get_instance()

        if not (image := self.graph.NonAVEntity.nodes.get_or_none(uuid=image_id)):
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise NotFound("Please specify a valid image id.")

        if not (item := image.item.single()):
            raise Conflict("Item not available. Execute the pipeline first!")

        if item.item_type != "Image":
            raise BadRequest("Content item is not a image. Use a valid image id.")

        repo = AnnotationRepository(self.graph)

        is_obj_detection = tool == "object-detection"
        is_building_recognition = tool == "building-recognition"

        if operation and operation == "delete":
            # get all automatic tags for selected tool
            deleted = 0
            annotations = item.sourcing_annotations.search(
                annotation_type="TAG", generator="FHG"
            )
            for anno in annotations:
                # expected always single body for automatic tags
                body = anno.bodies.single()

                labels = body.labels()

                if is_obj_detection and "ODBody" in labels and "BRBody" not in labels:
                    to_be_deleted = True
                elif is_building_recognition and "BRBody" in labels:
                    to_be_deleted = True
                else:
                    to_be_deleted = False

                if to_be_deleted:
                    deleted += 1
                    repo.delete_auto_annotation(anno)

            return self.response(
                f"There are no more automatic {tool} tags for image {image_id}."
                f"Deleted {deleted}",
            )

        if is_obj_detection:
            # DO NOT re-import object detection twice for the same image!
            if repo.check_automatic_od(item.uuid):
                raise Conflict(
                    "Object detection CANNOT be import twice for the same image"
                )
        elif is_building_recognition:

            # DO NOT re-import building recognition twice for the same image!
            if repo.check_automatic_br(item.uuid):
                raise Conflict(
                    "Building recognition CANNOT be import twice for the same image"
                )
        c = celery.get_instance()
        task = c.celery_app.send_task(
            "launch_tool", args=[tool, item.uuid], countdown=10
        )

        return self.response(task.id, code=202)
