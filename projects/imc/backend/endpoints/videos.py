"""
Handle your video entity
"""
import os  # still a lot of os. to be replaced with Pathlib
from pathlib import Path
from typing import Any, Dict, List, Optional

from imc.endpoints import IMCEndpoint
from imc.models import ShotRevision
from imc.security import authz
from imc.tasks.services.annotation_repository import AnnotationRepository
from imc.tasks.services.creation_repository import CreationRepository
from restapi import decorators
from restapi.config import get_backend_url
from restapi.connectors import celery, neo4j
from restapi.exceptions import BadRequest, Conflict, Forbidden, NotFound
from restapi.models import Schema, fields, validate
from restapi.rest.definition import Response
from restapi.services.authentication import Role, User
from restapi.services.download import Downloader
from restapi.utilities.logs import log


class VideoContentSchema(Schema):
    content_type = fields.Str(
        required=True,
        data_key="type",
        metadata={"description": "content type (e.g. video, thumbnail, summary)"},
        validate=validate.OneOf(["video", "orf", "thumbnail", "summary"]),
    )
    thumbnail_size = fields.Str(
        required=False,
        data_key="size",
        metadata={"description": "used to get large thumbnails"},
        validate=validate.OneOf(["large"]),
    )


class Videos(IMCEndpoint):

    labels = ["video"]

    @decorators.endpoint(
        path="/videos/<video_id>",
        summary="Get video metadata",
        description="Returns the requested video",
        responses={
            200: "Video successfully retrieved",
            404: "The video does not exist.",
        },
    )
    def get(self, video_id: str) -> Response:
        """Get the AVEntity passed as argument."""
        log.debug("getting AVEntity id: {}", video_id)
        graph = neo4j.get_instance()

        try:
            v = graph.AVEntity.nodes.get(uuid=video_id)
        except graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        api_url = get_backend_url()
        video = self.getJsonResponse(
            v,
            max_relationship_depth=1,
            relationships_expansion=[
                "record_sources.provider",
                "item.ownership",
                "item.revision",
                "item.other_version",
            ],
        )
        item = v.item.single()
        video["links"] = {}
        video["links"]["content"] = (
            api_url + "/api/videos/" + v.uuid + "/content?type=video"
        )
        if item.thumbnail is not None:
            video["links"]["thumbnail"] = (
                api_url + "/api/videos/" + v.uuid + "/content?type=thumbnail"
            )
        video["links"]["summary"] = (
            api_url + "/api/videos/" + v.uuid + "/content?type=summary"
        )

        return self.response(video)

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.database_transaction
    @decorators.endpoint(
        path="/videos/<video_id>",
        summary="Delete a video description",
        responses={200: "Video successfully deleted"},
    )
    def delete(self, video_id: str, user: User) -> Response:
        """
        Delete existing video description.
        """
        log.debug("deleting AVEntity id: {}", video_id)
        graph = neo4j.get_instance()

        if video_id is None:
            raise BadRequest("Please specify a valid video id")
        try:
            v = graph.AVEntity.nodes.get(uuid=video_id)
            repo = CreationRepository(graph)
            repo.delete_av_entity(v)
            return self.empty_response()
        except graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")


class VideoItem(IMCEndpoint):
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
        path="/videos/<video_id>/item",
        summary="Update public access flag for the given video",
        responses={
            204: "Item info successfully updated.",
            400: "Request not valid.",
            403: "Operation forbidden.",
            404: "Video does not exist.",
        },
    )
    def put(self, video_id: str, public_access: bool, user: User) -> Response:
        """
        Allow user to update item information.
        """
        log.debug("Update Item for AVEntity uuid: {}", video_id)

        graph = neo4j.get_instance()

        if not (video := graph.AVEntity.nodes.get_or_none(uuid=video_id)):
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            raise NotFound("AVEntity not correctly imported: item info not found")

        repo = CreationRepository(graph)
        if not repo.item_belongs_to_user(item, user):
            log.error("User {} not allowed to edit video {}", user.email, video_id)
            raise Forbidden(
                "Cannot update public access for videos that does not belong to you"
            )

        item.public_access = public_access
        item.save()
        log.debug("Item successfully updated for AVEntity uuid {}. {}", video_id, item)

        return self.empty_response()


class VideoAnnotations(IMCEndpoint):
    """
    Get all video annotations for a given video.
    """

    labels = ["video_annotations"]

    @decorators.use_kwargs(
        {
            "anno_type": fields.Str(
                required=False,
                data_key="type",
                metadata={"description": "Filter by annotation type (e.g. TAG)"},
                validate=validate.OneOf(["TAG", "DSC", "TVS"]),
            ),
            "is_manual": fields.Bool(
                required=False, load_default=False, data_key="onlyManual"
            ),
        },
        location="query",
    )
    @decorators.auth.require()
    @decorators.endpoint(
        path="/videos/<video_id>/annotations",
        summary="Gets video annotations",
        description="Returns all the annotations targeting the given video item.",
        responses={200: "An annotation object.", 404: "Video does not exist."},
    )
    def get(
        self,
        video_id: str,
        user: User,
        anno_type: Optional[str] = None,
        is_manual: bool = False,
    ) -> Response:
        log.debug("get annotations for AVEntity id: {}", video_id)

        graph = neo4j.get_instance()
        data = []

        video = None
        try:
            video = graph.AVEntity.nodes.get(uuid=video_id)
        except graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        item = video.item.single()
        for a in item.targeting_annotations:
            if anno_type is not None and a.annotation_type != anno_type:
                continue
            creator = a.creator.single()
            if is_manual and (creator is None or creator.uuid != user.uuid):
                continue
            if a.private:
                if creator is None:
                    log.warning(
                        "Invalid state: missing creator for private note [UUID:{}]",
                        a.uuid,
                    )
                    continue
                if creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(a, max_relationship_depth=0)
            if a.annotation_type in ("TAG", "DSC", "TVS") and a.creator is not None:
                res["creator"] = self.getJsonResponse(
                    a.creator.single(), max_relationship_depth=0
                )
            # attach bodies
            res["bodies"] = []
            for b in a.bodies.all():
                anno_body = b.downcast()
                body = self.getJsonResponse(anno_body, max_relationship_depth=0)
                if a.annotation_type == "TVS":
                    segments = []
                    for segment in anno_body.segments:
                        # look at the most derivative class
                        json_segment = self.getJsonResponse(
                            segment.downcast(), max_relationship_depth=0
                        )
                        # collect annotations and tags
                        # code duplicated for VideoShots.get
                        json_segment["annotations"] = []
                        json_segment["tags"] = []
                        # <dict(iri, name)>{iri, name, spatial, auto, hits}
                        tags: Dict[Any, Any] = {}
                        for anno in segment.annotation.all():
                            if anno.private:
                                if creator is None:
                                    log.warning(
                                        "Invalid state: missing creator for private "
                                        "note [UUID:{}]",
                                        anno.uuid,
                                    )
                                    continue
                                if creator is not None and creator.uuid != user.uuid:
                                    continue
                            s_anno = self.getJsonResponse(
                                anno, max_relationship_depth=0
                            )
                            if (
                                anno.annotation_type in ("TAG", "DSC")
                                and creator is not None
                            ):
                                s_anno["creator"] = self.getJsonResponse(
                                    anno.creator.single(), max_relationship_depth=0
                                )
                            # attach bodies
                            s_anno["bodies"] = []
                            for b in anno.bodies.all():
                                mdb = b.downcast()  # most derivative body
                                s_anno["bodies"].append(
                                    self.getJsonResponse(mdb, max_relationship_depth=0)
                                )
                                if anno.annotation_type == "TAG":
                                    spatial = None
                                    if "ResourceBody" in mdb.labels():
                                        iri = mdb.iri
                                        name = mdb.name
                                        spatial = mdb.spatial
                                    elif "TextualBody" in mdb.labels():
                                        iri = None
                                        name = mdb.value
                                    else:
                                        # unmanaged body type for tag
                                        continue
                                    """ only for manual tag annotations  """
                                    tag = tags.get((iri, name))
                                    if tag is None:
                                        tags[(iri, name)] = {
                                            "iri": iri,
                                            "name": name,
                                            "hits": 1,
                                        }
                                        if spatial is not None:
                                            tags[(iri, name)]["spatial"] = spatial
                                    else:
                                        tag["hits"] += 1
                            json_segment["annotations"].append(s_anno)
                        json_segment["tags"] = list(tags.values())
                        segments.append(json_segment)
                    body["segments"] = segments
                res["bodies"].append(body)
            data.append(res)

        return self.response(data)


class VideoShots(IMCEndpoint):
    """
    Get the list of shots for a given video.
    """

    labels = ["video_shots"]

    @decorators.auth.optional()
    @decorators.endpoint(
        path="/videos/<video_id>/shots",
        summary="Gets video shots",
        description="Returns a list of shots belonging to the given video item.",
        responses={200: "An list of shots.", 404: "Video does not exist."},
    )
    def get(self, video_id: str, user: Optional[User]) -> Response:
        log.debug("get shots for AVEntity id: {}", video_id)
        if video_id is None:
            raise BadRequest("Please specify a video id")

        graph = neo4j.get_instance()
        data = []

        video = None
        try:
            video = graph.AVEntity.nodes.get(uuid=video_id)
        except graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        item = video.item.single()
        api_url = get_backend_url()

        annotations: Dict[str, List[Any]] = {}

        annotations_query = (
            """
            MATCH (:AVEntity {uuid: '%s'})<-[:CREATION]-(:Item)-[:SHOT]->(shot:Shot)<-[:HAS_TARGET]-(anno:Annotation)-[:HAS_BODY]->(b:AnnotationBody)
            OPTIONAL MATCH (anno)-[:IS_ANNOTATED_BY]->(creator:User)
            RETURN shot.uuid, anno, creator, collect(b)
        """
            % video_id
        )

        log.debug("Prefetching annotations...")
        result = graph.cypher(annotations_query)
        for row in result:
            shot_uuid = row[0]

            annotation = graph.Annotation.inflate(row[1])
            if row[2] is not None:
                creator = graph.User.inflate(row[2])
            else:
                creator = None

            if annotation.private:
                if creator is None:
                    log.warning(
                        "Invalid state: missing creator for private note [UUID: {}]",
                        annotation.uuid,
                    )
                    continue
                if user is None:
                    continue
                if creator.uuid != user.uuid:
                    continue

            res = self.getJsonResponse(annotation, max_relationship_depth=0)

            # attach creator
            if annotation.annotation_type in ("TAG", "DSC", "LNK"):
                if creator is not None:
                    res["creator"] = self.getJsonResponse(
                        creator, max_relationship_depth=0
                    )

            # attach bodies
            res["bodies"] = []
            for concept in row[3]:
                b = graph.AnnotationBody.inflate(concept)
                b = b.downcast()  # most derivative body
                b_data = self.getJsonResponse(b, max_relationship_depth=0)
                res["bodies"].append(b_data)

            if shot_uuid not in annotations:
                annotations[shot_uuid] = []
            annotations[shot_uuid].append(res)

        log.debug("Prefetching automatic tags from embedded segments...")

        query_auto_tags = (
            """
            MATCH (:AVEntity {uuid: '%s'})<-[:CREATION]-(:Item)-[:SHOT]->(shot:Shot)-[:WITHIN_SHOT]-(sgm:VideoSegment)
            MATCH (sgm)<-[:HAS_TARGET]-(anno:Annotation {annotation_type:'TAG', generator:'FHG'})-[:HAS_BODY]-(b:ODBody)-[:CONCEPT]-(res:ResourceBody)
            RETURN shot.uuid, anno, collect(res)
        """
            % video_id
        )
        result = graph.cypher(query_auto_tags)
        for row in result:
            shot_uuid = row[0]
            if shot_uuid not in annotations:
                annotations[shot_uuid] = []

            auto_anno = graph.Annotation.inflate(row[1])
            res = self.getJsonResponse(auto_anno, max_relationship_depth=0)
            # attach bodies
            res["bodies"] = []
            for concept in row[2]:
                res["bodies"].append(
                    self.getJsonResponse(
                        graph.ResourceBody.inflate(concept),
                        max_relationship_depth=0,
                    )
                )
            annotations[shot_uuid].append(res)

        for s in item.shots.order_by("start_frame_idx"):
            shot = self.getJsonResponse(s)
            shot_url = api_url + "/api/shots/" + s.uuid
            shot["links"] = {}
            shot["links"]["thumbnail"] = shot_url + "?content=thumbnail"

            # Retrieving annotations from prefetched data
            shot["annotations"] = annotations.get(s.uuid, [])

            data.append(shot)

        return self.response(data)


class VideoContent(IMCEndpoint):

    labels = ["video"]

    @decorators.auth.optional()
    @decorators.use_kwargs(VideoContentSchema, location="query")
    @decorators.preload(callback=authz.check_permissions)
    @decorators.endpoint(
        path="/videos/<video_id>/content",
        summary="Gets the video content",
        responses={
            200: "Video content successfully retrieved",
            404: "The video content does not exists.",
        },
    )
    def get(
        self,
        video_id: str,
        content_type: str,
        user: Optional[User],
        thumbnail_size: Optional[str] = None,
    ) -> Response:
        """
        Gets video content such as video stream and thumbnail
        """
        log.debug("get video content for id {}", video_id)

        graph = neo4j.get_instance()
        video = None
        try:
            video = graph.AVEntity.nodes.get(uuid=video_id)
        except graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        item = video.item.single()
        if content_type == "video":
            # TODO manage here content access (see issue 190)
            # always return the other version if available
            video_uri = item.uri
            other_version = item.other_version.single()
            if other_version is not None:
                video_uri = other_version.uri
            log.debug("video content uri: {}", video_uri)
            if video_uri is None:
                raise NotFound("Video not found")
            # all videos are converted to mp4

            video_path = Path(video_uri)
            # return Downloader.send_file_partial(video_uri, mime)
            return Downloader.send_file_content(
                filename=video_path.name, subfolder=video_path.parent, mime="video/mp4"
            )

        if content_type == "orf":
            if item.uri is None:
                raise NotFound("Video ORF not found")

            folder = Path(item.uri).parent
            filename = "orf.mp4"
            if not folder.joinpath(filename).exists():
                raise NotFound("Video ORF not found")

            # return Downloader.send_file_partial(orf_uri, mime)
            return Downloader.send_file_content(
                filename=filename, subfolder=folder, mime="video/mp4"
            )

        if content_type == "thumbnail":
            thumbnail_uri = item.thumbnail
            log.debug("thumbnail content uri: {}", thumbnail_uri)

            # workaround when original thumbnail is renamed by revision procedure
            if not thumbnail_size and not os.path.exists(thumbnail_uri):
                log.debug("File {0} not found", thumbnail_uri)
                thumbnail_filename = os.path.basename(thumbnail_uri)
                thumbs_dir = os.path.dirname(thumbnail_uri)
                f_name, f_ext = os.path.splitext(thumbnail_filename)
                tokens = f_name.split("_")
                if len(tokens) > 0:
                    f = "f_" + tokens[-1] + f_ext
                    thumbnail_uri = os.path.join(thumbs_dir, f)

            # if thumbnail_size and thumbnail_size== "large":
            # large is the only allowed size at the moment
            if thumbnail_size:
                # load image file in the parent folder with the same name
                thumbnail_filename = os.path.basename(thumbnail_uri)
                thumbs_parent_dir = os.path.dirname(
                    os.path.dirname(os.path.abspath(thumbnail_uri))
                )
                thumbnail_uri = os.path.join(thumbs_parent_dir, thumbnail_filename)
                log.debug("request for large thumbnail: {}", thumbnail_uri)

            if thumbnail_uri is None or not os.path.exists(thumbnail_uri):
                raise NotFound("Thumbnail not found")

            thumbnail_path = Path(thumbnail_uri)
            return Downloader.send_file_content(
                filename=thumbnail_path.name,
                subfolder=thumbnail_path.parent,
                mime="image/jpeg",
            )

        if content_type == "summary":
            summary_uri = item.summary
            log.debug("summary content uri: {}", summary_uri)
            if summary_uri is None:
                raise NotFound("Summary not found")

            summary_path = Path(summary_uri)
            return Downloader.send_file_content(
                filename=summary_path.name,
                subfolder=summary_path.parent,
                mime="image/jpeg",
            )

        # it should never be reached
        raise BadRequest(f"Invalid content type: {content_type}")

    @decorators.use_kwargs(
        {
            "content_type": fields.Str(
                required=True,
                data_key="type",
                metadata={
                    "description": "content type (e.g. video, thumbnail, summary)"
                },
                validate=validate.OneOf(["video", "orf", "thumbnail", "summary"]),
            )
        },
        location="query",
    )
    @decorators.endpoint(
        path="/videos/<video_id>/content",
        summary="Check for video existence",
        responses={
            200: "The video content exists.",
            404: "The video content does not exists.",
        },
    )
    def head(self, video_id: str, content_type: str) -> Response:
        """
        Check for video content existance.
        """
        log.debug("check for video content existence with id {}", video_id)

        graph = neo4j.get_instance()
        video = None
        try:
            video = graph.AVEntity.nodes.get(uuid=video_id)
        except graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        item = video.item.single()
        headers = {}
        if content_type == "video":
            if item.uri is None or not os.path.exists(item.uri):
                raise NotFound("Video not found")
            headers["Content-Type"] = "video/mp4"
        elif content_type == "orf":
            orf_uri = os.path.dirname(item.uri) + "/orf.mp4"
            log.debug(orf_uri)
            if item.uri is None or not os.path.exists(orf_uri):
                raise NotFound("Video ORF not found")
            headers["Content-Type"] = "video/mp4"
        elif content_type == "thumbnail":
            if item.thumbnail is None or not os.path.exists(item.thumbnail):
                raise NotFound("Thumbnail not found")
            headers["Content-Type"] = "image/jpeg"
        elif content_type == "summary":
            if item.summary is None or not os.path.exists(item.summary):
                raise NotFound("Summary not found")
            headers["Content-Type"] = "image/jpeg"
        else:
            # it should never be reached
            raise BadRequest(f"Invalid content type: {content_type}")
        return self.response([], headers=headers)


class VideoTools(IMCEndpoint):

    labels = ["video_tools"]

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.use_kwargs(
        {
            "tool": fields.String(
                required=True,
                metadata={"description": "Tool to be launched."},
                validate=validate.OneOf(["object-detection", "building-recognition"]),
            ),
            "operation": fields.String(
                required=False,
                metadata={
                    "description": "At the moment used only to delete automatic tags."
                },
                validate=validate.OneOf(["delete"]),
            ),
        }
    )
    @decorators.endpoint(
        path="/videos/<video_id>/tools",
        summary="Allow to launch the execution of some video tools.",
        responses={
            202: "Execution task accepted.",
            200: "Execution completed successfully. only with delete operation.",
            403: "Request forbidden.",
            404: "Video not found.",
            409: "Invalid state. e.g. object detection results cannot be imported twice",
        },
    )
    def post(
        self, video_id: str, tool: str, user: User, operation: Optional[str] = None
    ) -> Response:

        log.debug("launch automatic tool for video id: {}", video_id)

        graph = neo4j.get_instance()

        if not (video := graph.AVEntity.nodes.get_or_none(uuid=video_id)):
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            raise Conflict("Item not available. Execute the pipeline first!")

        if item.item_type != "Video":
            raise BadRequest("Content item is not a video. Use a valid video id")

        repo = AnnotationRepository(graph)

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
                f"There are no more automatic {tool} tags for video {video_id}."
                f"Deleted {deleted}"
            )

        if is_obj_detection:
            # DO NOT re-import object detection twice for the same video!
            if repo.check_automatic_od(item.uuid):
                raise Conflict(
                    "Object detection CANNOT be import twice for the same video"
                )
        elif is_building_recognition:

            # DO NOT re-import building recognition twice for the same video!
            if repo.check_automatic_br(item.uuid):
                raise Conflict(
                    "Building recognition CANNOT be import twice for the same video"
                )

        c = celery.get_instance()
        task = c.celery_app.send_task(
            "launch_tool",
            args=(
                tool,
                item.uuid,
            ),
            countdown=10,
        )

        return self.response(task.id, code=202)


class VideoShotRevision(IMCEndpoint):
    """Shot revision endpoint"""

    labels = ["video_shot_revision"]

    # "schema": {
    #     "type": "array",      -> many=True
    #     "items": {"$ref": "#/definitions/VideoInRevision"},
    # },

    # This is the model semi-translated in marshmallow, to be completed:
    # since = fields.fields.DateTime(required=True, metadata={"description": "Date of start of a revision."})
    # video = fields.Nested( ..., required=True, metadata={"description": "Video under revision"})
    #                       uuid = fields.UUID(required=True)
    #                       title = fields.Str(required=True)
    # progress = fields.Int(required=True, metadata={"description": "Progress of the revision in percentange", validate = min 0 max 100})
    # state = fields.Str(required=True, metadata={"description": "Revision status"}, validate = oneOf ["R", "W"]
    # assignee = fields.Nested( ... , required=True, metadata={"description": "assignee of the revision"})
    #                           uuid = fields.UUID(required=True)
    #                           name = fields.Str(required=True)
    @decorators.auth.require_any(Role.ADMIN, "Reviser")
    @decorators.use_kwargs(
        {
            "input_assignee": fields.Str(
                required=False,
                data_key="assignee",
                metadata={"description": "Assignee's uuid of the revision"},
            )
        },
        location="query",
    )
    @decorators.endpoint(
        path="/videos-under-revision",
        summary="List of videos under revision.",
        description="Returns a list of all videos under revision and their assignee",
        responses={200: "List of videos under revision successfully retrieved"},
    )
    def get(self, user: User, input_assignee: Optional[str] = None) -> Response:
        """Get all videos under revision"""
        log.debug("Getting videos under revision.")
        graph = neo4j.get_instance()
        data = []

        # naive solution for getting VideoInRevision
        items = graph.Item.nodes.has(revision=True)
        for i in items:
            creation = i.creation.single()
            video = creation.downcast()
            assignee = i.revision.single()
            if input_assignee is not None and input_assignee != assignee.uuid:
                continue
            rel = i.revision.relationship(assignee)
            shots = i.shots.all()
            number_of_shots = len(shots)
            number_of_confirmed = len([s for s in shots if s.revision_confirmed])
            percentage = 100 * number_of_confirmed / number_of_shots
            res = {
                "video": {"uuid": video.uuid, "title": video.identifying_title},
                "assignee": {
                    "uuid": assignee.uuid,
                    "name": assignee.name + " " + assignee.surname,
                },
                "since": rel.when.isoformat(),
                "state": rel.state,
                "progress": percentage,
            }
            data.append(res)

        return self.response(data)

    @decorators.auth.require_any(Role.ADMIN, "Reviser")
    @decorators.database_transaction
    @decorators.use_kwargs(
        {
            "assignee_uuid": fields.Str(
                required=False,
                metadata={
                    "description": "UUID of the Reviser user to assign the revision"
                },
                data_key="assignee",
            )
        }
    )
    @decorators.endpoint(
        path="/videos/<video_id>/shot-revision",
        summary="Put a video under revision",
        responses={
            204: "Video under revision successfully.",
            400: "Assignee not valid.",
            409: "Video is already under revision or it is not ready for revision.",
            403: "Operation forbidden.",
            404: "Video does not exist.",
        },
    )
    def put(
        self, video_id: str, user: User, assignee_uuid: Optional[str] = None
    ) -> Response:
        """Put a video under revision"""
        log.debug("Put video {} under revision", video_id)

        graph = neo4j.get_instance()
        if not (video := graph.AVEntity.nodes.get_or_none(uuid=video_id)):
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            raise Forbidden(
                "This AVEntity may not have been correctly imported. "
                "Not ready for revision!",
            )

        i_am_admin = self.auth.is_admin(user)

        log.debug(
            "Request for revision from user [{}, {} {}]",
            user.uuid,
            user.name,
            user.surname,
        )
        # Be sure user can revise this specific video

        # allow admin to pass the assignee
        if i_am_admin and assignee_uuid:
            assignee = graph.User.nodes.get_or_none(uuid=assignee_uuid)
        else:
            assignee = user

        if not assignee:
            raise NotFound(f"Invalid candidate. User [{assignee_uuid}] does not exist")

        assignee_is_admin = self.auth.is_admin(assignee)

        log.debug("Assignee is admin? {}", assignee_is_admin)

        repo = CreationRepository(graph)

        if not assignee_is_admin and not repo.item_belongs_to_user(item, assignee):
            raise Forbidden(
                f"User [{user.uuid}, {user.name} {user.surname}] cannot revise video "
                "that does not belong to him/her"
            )
        if repo.is_video_under_revision(item):
            raise Conflict(f"Video [{video.uuid}] is already under revision")

        repo.move_video_under_revision(item, assignee)
        return self.empty_response()

    @decorators.auth.require_any(Role.ADMIN, "Reviser")
    @decorators.use_kwargs(ShotRevision)
    @decorators.endpoint(
        path="/videos/<video_id>/shot-revision",
        summary="Launch the execution of the shot revision tool.",
        responses={
            201: "Execution launched.",
            403: "Request forbidden.",
            404: "Video not found.",
            409: "Invalid state for the video.",
        },
    )
    def post(
        self, video_id: str, shots: List[Any], exitRevision: bool, user: User
    ) -> Response:
        """Start a shot revision procedure"""
        log.debug("Start shot revision for video {}", video_id)

        graph = neo4j.get_instance()

        video = graph.AVEntity.nodes.get_or_none(uuid=video_id)
        if not video:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            # 409: Video is not ready for revision. (should never be reached)
            raise Conflict(
                "AVEntity not correctly imported: not ready for revision!",
            )

        repo = CreationRepository(graph)
        # be sure video is under revision
        if not repo.is_video_under_revision(item):
            raise Conflict(
                f"This video [{video_id}] is not under revision!",
            )

        # ONLY the reviser and the administrator can provide a new list of cuts
        i_am_admin = self.auth.is_admin(user)
        if not i_am_admin and not repo.is_revision_assigned_to_user(item, user):
            raise Forbidden("You cannot revise a video that is not owned by you")

        revision = {
            "shots": shots,
            "exitRevision": exitRevision,
            "reviser": user.uuid,
        }

        # launch async task
        try:
            c = celery.get_instance()
            task = c.celery_app.send_task(
                "shot_revision",
                args=(
                    revision,
                    item.uuid,
                ),
                countdown=10,
                priority=5,
            )
            assignee = item.revision.single()
            rel = item.revision.relationship(assignee)
            rel.state = "R"
            rel.save()
            # 202: OK_ACCEPTED
            return self.response(task.id, code=202)
        except BaseException as e:
            raise e

    @decorators.auth.require_any(Role.ADMIN, "Reviser")
    @decorators.endpoint(
        path="/videos/<video_id>/shot-revision",
        summary="Take off revision from a video.",
        responses={
            204: "Video revision successfully exited.",
            403: "Request forbidden.",
            404: "Video not found.",
        },
    )
    def delete(self, video_id: str, user: User) -> Response:
        """Take off revision from a video"""
        log.debug("Exit revision for video {0}", video_id)

        graph = neo4j.get_instance()
        video = graph.AVEntity.nodes.get_or_none(uuid=video_id)
        if not video:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            # 409: Video is not ready for revision. (should never be reached)
            raise Conflict("AVEntity not correctly imported: not ready for revision!")

        repo = CreationRepository(graph)
        if not repo.is_video_under_revision(item):
            # 409: Video is already under revision.
            raise BadRequest(f"Video [{video.uuid}] is not under revision")

        # ONLY the reviser and the administrator can exit revision
        i_am_admin = self.auth.is_admin(user)
        if not i_am_admin and not repo.is_revision_assigned_to_user(item, user):
            raise Forbidden(
                f"User [{user.uuid}, {user.name} {user.surname}] cannot exit"
                " revision for video that is not assigned to him/her",
            )

        repo.exit_video_under_revision(item)
        # 204: Video revision successfully exited.
        return self.empty_response()
