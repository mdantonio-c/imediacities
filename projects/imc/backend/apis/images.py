"""
Handle your image entity
"""
import os

from flask import send_file
from imc.apis import IMCEndpoint
from imc.security import authz
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.tasks.services.creation_repository import CreationRepository
from restapi import decorators
from restapi.confs import get_backend_url
from restapi.connectors.neo4j import graph_transactions
from restapi.exceptions import RestApiException
from restapi.models import fields, validate
from restapi.services.download import Downloader
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


#####################################
class Images(IMCEndpoint):

    """
    Get an NonAVEntity if its id is passed as an argument.
    Else return all NonAVEntities in the repository.
    """

    labels = ["image"]
    _GET = {
        "/images/<image_id>": {
            "summary": "List of images",
            "description": "Returns a list containing all images. The list supports paging.",
            "responses": {
                "200": {"description": "List of images successfully retrieved"},
                "404": {"description": "The image does not exists."},
            },
        },
        "/images": {
            "summary": "List of images",
            "description": "Returns a list containing all images. The list supports paging.",
            "responses": {
                "200": {"description": "List of images successfully retrieved"},
                "404": {"description": "The image does not exists."},
            },
        },
    }
    _POST = {
        "/images": {
            "summary": "Create a new image description",
            "description": "Simple method to attach descriptive metadata to a previously uploaded image (item).",
            "responses": {
                "200": {"description": "Image description successfully created"}
            },
        }
    }
    _DELETE = {
        "/images/<image_id>": {
            "summary": "Delete a image description",
            "responses": {"200": {"description": "Image successfully deleted"}},
        }
    }

    @decorators.catch_graph_exceptions
    def get(self, image_id=None):

        if image_id is None and not self.verify_admin():
            raise RestApiException(
                "You are not authorized", status_code=hcodes.HTTP_BAD_FORBIDDEN
            )

        log.debug("getting NonAVEntity id: {}", image_id)
        self.graph = self.get_service_instance("neo4j")
        data = []

        if image_id is not None:
            # check if the image exists
            try:
                v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
            except self.graph.NonAVEntity.DoesNotExist:
                log.debug("NonAVEntity with uuid {} does not exist", image_id)
                raise RestApiException(
                    "Please specify a valid image id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND,
                )
            images = [v]
        else:
            images = self.graph.NonAVEntity.nodes.all()

        host = get_backend_url()
        for v in images:
            image = self.getJsonResponse(
                v,
                max_relationship_depth=1,
                relationships_expansion=["record_sources.provider", "item.ownership"],
            )
            item = v.item.single()
            image_url = f"{host}/api/images/{v.uuid}/content?type=image"
            image["links"]["content"] = image_url
            if item.thumbnail is not None:
                thumbnail_url = f"{host}/api/images/{v.uuid}/content?type=thumbnail"
                image["links"]["thumbnail"] = thumbnail_url
            summary_url = f"{host}/api/images/{v.uuid}/content?type=summary"
            image["links"]["summary"] = summary_url
            data.append(image)

        return self.response(data)

    """
    Create a new image description.
    """

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.require()
    def post(self):
        self.graph = self.get_service_instance("neo4j")

        return self.empty_response()

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=["admin_root"])
    def delete(self, image_id):
        """
        Delete existing image description.
        """
        log.debug("deliting NonAVEntity id: {}", image_id)
        self.graph = self.get_service_instance("neo4j")

        if image_id is None:
            raise RestApiException(
                "Please specify a valid image id", status_code=hcodes.HTTP_BAD_REQUEST
            )
        try:
            v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
            repo = CreationRepository(self.graph)
            repo.delete_non_av_entity(v)
            return self.empty_response()
        except self.graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise RestApiException(
                "Please specify a valid image id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )


class ImageItem(IMCEndpoint):

    _PUT = {
        "/images/<image_id>/item": {
            "summary": "Update item info. At the moment ONLY used for the public access flag",
            "parameters": [
                {
                    "name": "item_update",
                    "in": "body",
                    "description": "The item properties to be updated.",
                    "schema": {
                        "properties": {
                            "public_access": {
                                "description": "Whether or not the item is accessible by a public user.",
                                "type": "boolean",
                            }
                        }
                    },
                }
            ],
            "responses": {
                "204": {"description": "Item info successfully updated."},
                "400": {"description": "Request not valid."},
                "403": {"description": "Operation forbidden."},
                "404": {"description": "Image does not exist."},
            },
        }
    }

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=["Archive", "admin_root"], required_roles="any")
    def put(self, image_id):
        """
        Allow user to update item information.
        """
        log.debug("Update Item for NonAVEntity uuid: {}", image_id)
        if image_id is None:
            raise RestApiException(
                "Please specify a image id", status_code=hcodes.HTTP_BAD_REQUEST
            )
        self.graph = self.get_service_instance("neo4j")
        try:
            v = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise RestApiException(
                "Please specify a valid image id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        item = v.item.single()
        if item is None:
            raise RestApiException(
                "This NonAVEntity may not have been correctly imported. "
                "Item info not found",
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )

        user = self.get_user()
        repo = CreationRepository(self.graph)
        if not repo.item_belongs_to_user(item, user):
            raise RestApiException(
                "User [{}, {} {}] cannot update public access for videos that does not belong to him/her".format(
                    user.uuid, user.name, user.surname
                ),
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        data = self.get_input()
        # ONLY public_access allowed at the moment
        public_access = data.get("public_access")
        if public_access is None or type(public_access) != bool:
            raise RestApiException(
                "Please specify a valid value for public_access",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        item.public_access = public_access
        item.save()
        log.debug(
            "Item successfully updated for NonAVEntity uuid {}. {}", image_id, item
        )

        # 204: Item successfully updated.
        return self.empty_response()


class ImageAnnotations(IMCEndpoint):
    """
        Get all image annotations for a given image.
    """

    labels = ["image_annotations"]
    _GET = {
        "/images/<image_id>/annotations": {
            "summary": "Gets image annotations",
            "description": "Returns all the annotations targeting the given image item.",
            "responses": {
                "200": {"description": "An annotation object."},
                "404": {"description": "Image does not exist."},
            },
        }
    }

    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {
            "anno_type": fields.Str(
                required=False,
                data_key="type",
                description="Filter by annotation type (e.g. TAG, DSC)",
                validate=validate.OneOf(["TAG", "DSC"]),
            )
        },
        locations=["query"],
    )
    def get(self, image_id, anno_type=None):
        log.debug("get annotations for NonAVEntity id: {}", image_id)

        self.graph = self.get_service_instance("neo4j")
        data = []

        image = self.graph.NonAVEntity.nodes.get_or_none(uuid=image_id)
        if not image:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise RestApiException(
                "Please specify a valid image id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

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
    """
    Gets image content or thumbnail
    """

    labels = ["image"]
    _GET = {
        "/images/<image_id>/content": {
            "summary": "Gets the image content",
            "responses": {
                "200": {"description": "Image content successfully retrieved"},
                "404": {"description": "The image content does not exists."},
            },
        }
    }

    @decorators.catch_graph_exceptions
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
        locations=["query"],
    )
    @authz.pre_authorize
    def get(self, image_id, content_type, thumbnail_size=None):
        log.info("get image content for id {}", image_id)

        self.graph = self.get_service_instance("neo4j")
        image = None
        try:
            image = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise RestApiException(
                "Please specify a valid image id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        item = image.item.single()
        log.debug("item data: " + format(item))
        if content_type == "image":
            # TODO manage here content access (see issue 190)
            # always return the other version if available
            image_uri = item.uri
            other_version = item.other_version.single()
            if other_version is not None:
                image_uri = other_version.uri
            log.debug("image content uri: {}", image_uri)
            if image_uri is None:
                raise RestApiException(
                    "Image not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
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
                raise RestApiException(
                    "Thumbnail not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            return send_file(thumbnail_uri, mimetype="image/jpeg")

        # it should never be reached
        raise RestApiException(
            f"Invalid content type: {content_type}",
            status_code=hcodes.HTTP_NOT_IMPLEMENTED,
        )


class ImageTools(IMCEndpoint):

    __available_tools__ = ("object-detection", "building-recognition")
    labels = ["image_tools"]
    _POST = {
        "/images/<image_id>/tools": {
            "summary": "Allow to launch the execution of some image tools.",
            "parameters": [
                {
                    "name": "criteria",
                    "in": "body",
                    "description": "Criteria to launch the tool.",
                    "schema": {
                        "required": ["tool"],
                        "properties": {
                            "tool": {
                                "description": "Tool to be launched.",
                                "type": "string",
                                "enum": ["object-detection", "building-recognition"],
                            },
                            "operation": {
                                "description": "At the moment used only to delete automatic tags.",
                                "type": "string",
                                "enum": ["delete"],
                            },
                        },
                    },
                }
            ],
            "responses": {
                "202": {"description": "Execution task accepted."},
                "200": {
                    "description": "Execution completed successfully. Only with delete operation."
                },
                "403": {"description": "Request forbidden."},
                "404": {"description": "Image not found."},
                "409": {
                    "description": "Invalid state. E.g. object detection results cannot be imported twice."
                },
            },
        }
    }

    @decorators.catch_graph_exceptions
    @decorators.auth.required(roles=["admin_root"])
    def post(self, image_id):

        log.debug("launch automatic tool for image id: {}", image_id)

        if image_id is None:
            raise RestApiException(
                "Please specify a image id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance("neo4j")
        celery = self.get_service_instance("celery")
        image = None
        try:
            image = self.graph.NonAVEntity.nodes.get(uuid=image_id)
        except self.graph.NonAVEntity.DoesNotExist:
            log.debug("NonAVEntity with uuid {} does not exist", image_id)
            raise RestApiException(
                "Please specify a valid image id.", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        item = image.item.single()
        if item is None:
            raise RestApiException(
                "Item not available. Execute the pipeline first!",
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )
        if item.item_type != "Image":
            raise RestApiException(
                "Content item is not a image. Use a valid image id.",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        params = self.get_input()
        if "tool" not in params:
            raise RestApiException(
                "Please specify the tool to be launched.",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        tool = params["tool"]
        if tool not in self.__available_tools__:
            raise RestApiException(
                "Please specify a valid tool. Expected one of {}".format(
                    self.__available_tools__
                ),
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        repo = AnnotationRepository(self.graph)
        if tool == self.__available_tools__[0]:  # object-detection
            if "operation" in params and params["operation"] == "delete":
                # get all automatic object detection tags
                deleted = 0
                for anno in item.sourcing_annotations.search(
                    annotation_type="TAG", generator="FHG"
                ):
                    # expected always single body for automatic tags
                    body = anno.bodies.single()
                    if "ODBody" in body.labels() and "BRBody" not in body.labels():
                        deleted += 1
                        repo.delete_auto_annotation(anno)
                return self.response(
                    "There are no more automatic object detection tags for image {}. Deleted {}".format(
                        image_id, deleted
                    ),
                    code=hcodes.HTTP_OK_BASIC,
                )
            # DO NOT re-import object detection twice for the same image!
            if repo.check_automatic_od(item.uuid):
                raise RestApiException(
                    "Object detection CANNOT be import twice for the same image.",
                    status_code=hcodes.HTTP_BAD_CONFLICT,
                )
        elif tool == self.__available_tools__[1]:  # building-recognition
            if "operation" in params and params["operation"] == "delete":
                # get all automatic building recognition tags
                deleted = 0
                for anno in item.sourcing_annotations.search(
                    annotation_type="TAG", generator="FHG"
                ):
                    # expected always single body for automatic tags
                    body = anno.bodies.single()
                    if "BRBody" in body.labels():
                        deleted += 1
                        repo.delete_auto_annotation(anno)
                return self.response(
                    "There are no more automatic building recognition tags for image {}. Deleted {}".format(
                        image_id, deleted
                    ),
                    code=hcodes.HTTP_OK_BASIC,
                )
            # DO NOT re-import building recognition twice for the same image!
            if repo.check_automatic_br(item.uuid):
                raise RestApiException(
                    "Building recognition CANNOT be import twice for the same image.",
                    status_code=hcodes.HTTP_BAD_CONFLICT,
                )
        else:
            # should never be reached
            raise RestApiException(
                f"Specified tool '{tool}' NOT implemented",
                status_code=hcodes.HTTP_NOT_IMPLEMENTED,
            )

        task = celery.launch_tool.apply_async(args=[tool, item.uuid], countdown=10)

        return self.response(task.id, code=hcodes.HTTP_OK_ACCEPTED)
