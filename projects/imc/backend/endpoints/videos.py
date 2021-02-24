"""
Handle your video entity
"""
import os

from flask import send_file
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
from restapi.services.authentication import Role
from restapi.services.download import Downloader
from restapi.utilities.logs import log


class VideoContentSchema(Schema):
    content_type = fields.Str(
        required=True,
        data_key="type",
        description="content type (e.g. video, thumbnail, summary)",
        validate=validate.OneOf(["video", "orf", "thumbnail", "summary"]),
    )
    thumbnail_size = fields.Str(
        required=False,
        data_key="size",
        description="used to get large thumbnails",
        validate=validate.OneOf(["large"]),
    )


class Videos(IMCEndpoint):

    """
    Get an AVEntity if its id is passed as an argument.
    Else return all AVEntities in the repository.
    """

    labels = ["video"]

    @decorators.auth.optional()
    @decorators.endpoint(
        path="/videos/<video_id>",
        summary="List of videos",
        description="Returns the requested video",
        responses={
            200: "Video successfully retrieved",
            404: "The video does not exists.",
        },
    )
    @decorators.endpoint(
        path="/videos",
        summary="List of videos",
        description="Returns a list containing all videos",
        responses={
            200: "List of videos successfully retrieved",
            403: "Operation not authorized",
            404: "The video does not exists",
        },
    )
    def get(self, video_id=None):

        if video_id is None and not self.verify_admin():
            raise Forbidden("You are not authorized")

        log.debug("getting AVEntity id: {}", video_id)
        self.graph = neo4j.get_instance()
        data = []

        if video_id is not None:
            # check if the video exists
            try:
                v = self.graph.AVEntity.nodes.get(uuid=video_id)
            except self.graph.AVEntity.DoesNotExist:
                log.debug("AVEntity with uuid {} does not exist", video_id)
                raise NotFound("Please specify a valid video id")
            videos = [v]
        else:
            videos = self.graph.AVEntity.nodes.all()

        api_url = get_backend_url()
        for v in videos:
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
            data.append(video)

        return self.response(data)

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.database_transaction
    @decorators.endpoint(
        path="/videos/<video_id>",
        summary="Delete a video description",
        responses={200: "Video successfully deleted"},
    )
    def delete(self, video_id):
        """
        Delete existing video description.
        """
        log.debug("deleting AVEntity id: {}", video_id)
        self.graph = neo4j.get_instance()

        if video_id is None:
            raise BadRequest("Please specify a valid video id")
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
            repo = CreationRepository(self.graph)
            repo.delete_av_entity(v)
            return self.empty_response()
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")


class VideoItem(IMCEndpoint):
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
        path="/videos/<video_id>/item",
        summary="Update public access flag for the given video",
        responses={
            204: "Item info successfully updated.",
            400: "Request not valid.",
            403: "Operation forbidden.",
            404: "Video does not exist.",
        },
    )
    def put(self, video_id, public_access):
        """
        Allow user to update item information.
        """
        log.debug("Update Item for AVEntity uuid: {}", video_id)

        self.graph = neo4j.get_instance()

        if not (video := self.graph.AVEntity.nodes.get_or_none(uuid=video_id)):
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            raise NotFound("AVEntity not correctly imported: item info not found")

        user = self.get_user()
        repo = CreationRepository(self.graph)
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
                description="Filter by annotation type (e.g. TAG)",
                validate=validate.OneOf(["TAG", "DSC", "TVS"]),
            ),
            "is_manual": fields.Bool(
                required=False, missing=False, data_key="onlyManual"
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
    def get(self, video_id, anno_type=None, is_manual=False):
        log.debug("get annotations for AVEntity id: {}", video_id)

        self.graph = neo4j.get_instance()
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        user = self.get_user()

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
                        tags = {}
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
    def get(self, video_id):
        log.debug("get shots for AVEntity id: {}", video_id)
        if video_id is None:
            raise BadRequest("Please specify a video id")

        self.graph = neo4j.get_instance()
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        user = self.get_user()

        item = video.item.single()
        api_url = get_backend_url()

        annotations = {}

        annotations_query = (
            """
            MATCH (:AVEntity {uuid: '%s'})<-[:CREATION]-(:Item)-[:SHOT]->(shot:Shot)<-[:HAS_TARGET]-(anno:Annotation)-[:HAS_BODY]->(b:AnnotationBody)
            OPTIONAL MATCH (anno)-[:IS_ANNOTATED_BY]->(creator:User)
            RETURN shot.uuid, anno, creator, collect(b)
        """
            % video_id
        )

        log.debug("Prefetching annotations...")
        result = self.graph.cypher(annotations_query)
        for row in result:
            shot_uuid = row[0]

            annotation = self.graph.Annotation.inflate(row[1])
            if row[2] is not None:
                creator = self.graph.User.inflate(row[2])
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
                b = self.graph.AnnotationBody.inflate(concept)
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
        result = self.graph.cypher(query_auto_tags)
        for row in result:
            shot_uuid = row[0]
            if shot_uuid not in annotations:
                annotations[shot_uuid] = []

            auto_anno = self.graph.Annotation.inflate(row[1])
            res = self.getJsonResponse(auto_anno, max_relationship_depth=0)
            # attach bodies
            res["bodies"] = []
            for concept in row[2]:
                res["bodies"].append(
                    self.getJsonResponse(
                        self.graph.ResourceBody.inflate(concept),
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


class VideoSegments(IMCEndpoint):
    """
    Get the list of manual segments for a given video.
    """

    labels = ["video_segments", "video-segment"]

    @decorators.auth.require()
    @decorators.endpoint(
        path="/videos/<video_id>/segments/<segment_id>",
        summary="Gets all manual segments for a video.",
        description="Returns a list of manual segments belonging to the given video item",
        responses={200: "An list of manual segments.", 404: "Video does not exist."},
    )
    @decorators.endpoint(
        path="/videos/<video_id>/segments",
        summary="Gets all manual segments for a video.",
        description="Returns a list of manual segments belonging to the given video item",
        responses={200: "An list of manual segments.", 404: "Video does not exist."},
    )
    def get(self, video_id, segment_id):

        log.debug("get all manual segments for AVEntity [uuid:{}]", video_id)

        self.graph = neo4j.get_instance()

        video = self.graph.AVEntity.nodes.get_or_None(uuid=video_id)
        if not video:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        # user = self.get_user()

        item = video.item.single()
        log.debug("get manual segments for Item [{}]", item.uuid)

        data = []
        # TODO

        return self.response(data)


class VideoContent(IMCEndpoint, Downloader):

    labels = ["video"]

    @decorators.auth.optional()
    @decorators.use_kwargs(VideoContentSchema, location="query")
    @decorators.endpoint(
        path="/videos/<video_id>/content",
        summary="Gets the video content",
        responses={
            200: "Video content successfully retrieved",
            404: "The video content does not exists.",
        },
    )
    @authz.pre_authorize
    def get(self, video_id, content_type, thumbnail_size=None):
        """
        Gets video content such as video strem and thumbnail
        """
        log.debug("get video content for id {}", video_id)

        self.graph = neo4j.get_instance()
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
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

            filename = os.path.basename(video_uri)
            folder = os.path.dirname(video_uri)
            # return self.send_file_partial(video_uri, mime)
            return self.download(filename=filename, subfolder=folder, mime="video/mp4")

        if content_type == "orf":
            # orf_uri = os.path.dirname(item.uri) + '/transcoded_orf.mp4'
            if item.uri is None:
                raise NotFound("Video ORF not found")

            folder = os.path.dirname(item.uri)
            filename = "orf.mp4"
            # orf_uri = os.path.dirname(item.uri) + '/orf.mp4'
            # if orf_uri is None or not os.path.exists(orf_uri):
            if not os.path.exists(os.path.join(folder, filename)):
                raise NotFound("Video ORF not found")

            # return self.send_file_partial(orf_uri, mime)
            return self.download(filename=filename, subfolder=folder, mime="video/mp4")

        if content_type == "thumbnail":
            thumbnail_uri = item.thumbnail
            log.debug("thumbnail content uri: {}", thumbnail_uri)

            # workaround when original thumnail is renamed by revision procedure
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
            return send_file(thumbnail_uri, mimetype="image/jpeg")

        if content_type == "summary":
            summary_uri = item.summary
            log.debug("summary content uri: {}", summary_uri)
            if summary_uri is None:
                raise NotFound("Summary not found")
            return send_file(summary_uri, mimetype="image/jpeg")

        # it should never be reached
        raise BadRequest(f"Invalid content type: {content_type}")

    @decorators.database_transaction
    @decorators.use_kwargs(
        {
            "content_type": fields.Str(
                required=True,
                data_key="type",
                description="content type (e.g. video, thumbnail, summary)",
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
    def head(self, video_id, content_type):
        """
        Check for video content existance.
        """
        log.debug("check for video content existence with id {}", video_id)

        self.graph = neo4j.get_instance()
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
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
    def post(self, video_id, tool, operation=None):

        log.debug("launch automatic tool for video id: {}", video_id)

        self.graph = neo4j.get_instance()

        if not (video := self.graph.AVEntity.nodes.get_or_none(uuid=video_id)):
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            raise Conflict("Item not available. Execute the pipeline first!")

        if item.item_type != "Video":
            raise BadRequest("Content item is not a video. Use a valid video id")

        repo = AnnotationRepository(self.graph)

        OBJ_DETECTION = tool == "object-detection"
        BUILDING_RECOGNITION = tool == "building-recognition"

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

                if OBJ_DETECTION and "ODBody" in labels and "BRBody" not in labels:
                    to_be_deleted = True
                elif BUILDING_RECOGNITION and "BRBody" in labels:
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

        if OBJ_DETECTION:
            # DO NOT re-import object detection twice for the same video!
            if repo.check_automatic_od(item.uuid):
                raise Conflict(
                    "Object detection CANNOT be import twice for the same video"
                )
        elif BUILDING_RECOGNITION:

            # DO NOT re-import building recognition twice for the same video!
            if repo.check_automatic_br(item.uuid):
                raise Conflict(
                    "Building recognition CANNOT be import twice for the same video"
                )

        c = celery.get_instance()
        task = c.celery_app.send_task(
            "launch_tool", args=[tool, item.uuid], countdown=10
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
    # since = fields.fields.DateTime(required=True, description="Date of start of a revision.")
    # video = fields.Nested( ..., required=True, description="Video under revision")
    #                       uuid = fields.UUID(required=True)
    #                       title = fields.Str(required=True)
    # progress = fields.Int(required=True, description="Progress of the revision in percentange", validate = min 0 max 100)
    # state = fields.Str(required=True, description="Revision status", validate = oneOf ["R", "W"]
    # assignee = fields.Nested( ... , required=True, description="assignee of the revision")
    #                           uuid = fields.UUID(required=True)
    #                           name = fields.Str(required=True)
    @decorators.auth.require_any(Role.ADMIN, "Reviser")
    @decorators.use_kwargs(
        {
            "input_assignee": fields.Str(
                required=False,
                data_key="assignee",
                description="Assignee's uuid of the revision",
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
    def get(self, input_assignee=None):
        """Get all videos under revision"""
        log.debug("Getting videos under revision.")
        self.graph = neo4j.get_instance()
        data = []

        # naive solution for getting VideoInRevision
        items = self.graph.Item.nodes.has(revision=True)
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
                description="UUID of the Reviser user to assign the revision",
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
    def put(self, video_id, assignee_uuid=None):
        """Put a video under revision"""
        log.debug("Put video {} under revision", video_id)

        self.graph = neo4j.get_instance()
        if not (video := self.graph.AVEntity.nodes.get_or_none(uuid=video_id)):
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            raise Forbidden(
                "This AVEntity may not have been correctly imported. "
                "Not ready for revision!",
            )

        user = self.get_user()
        iamadmin = self.verify_admin()

        log.debug(
            "Request for revision from user [{}, {} {}]",
            user.uuid,
            user.name,
            user.surname,
        )
        # Be sure user can revise this specific video

        # allow admin to pass the assignee
        if iamadmin and assignee_uuid:
            assignee = self.graph.User.nodes.get_or_none(uuid=assignee_uuid)
            if not assignee:
                raise NotFound(
                    f"Invalid candidate. User [{assignee_uuid}] does not exist"
                )

            assignee_is_admin = self.auth.verify_roles(
                assignee, [Role.ADMIN], warnings=False
            )
        else:
            assignee = user
            assignee_is_admin = iamadmin

        log.debug("Assignee is admin? {}", assignee_is_admin)

        repo = CreationRepository(self.graph)

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
    def post(self, video_id, shots, exitRevision):
        """Start a shot revision procedure"""
        log.debug("Start shot revision for video {0}", video_id)

        self.graph = neo4j.get_instance()

        video = self.graph.AVEntity.nodes.get_or_none(uuid=video_id)
        if not video:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            # 409: Video is not ready for revision. (should never be reached)
            raise Conflict(
                "AVEntity not correctly imported: not ready for revision!",
            )

        repo = CreationRepository(self.graph)
        # be sure video is under revision
        if not repo.is_video_under_revision(item):
            raise Conflict(
                f"This video [{video_id}] is not under revision!",
            )

        # ONLY the reviser and the administrator can provide a new list of cuts
        user = self.get_user()
        iamadmin = self.verify_admin()
        if not iamadmin and not repo.is_revision_assigned_to_user(item, user):
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
                "shot_revision", args=[revision, item.uuid], countdown=10, priority=5
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
    def delete(self, video_id):
        """Take off revision from a video"""
        log.debug("Exit revision for video {0}", video_id)

        self.graph = neo4j.get_instance()
        video = self.graph.AVEntity.nodes.get_or_none(uuid=video_id)
        if not video:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise NotFound("Please specify a valid video id")

        if not (item := video.item.single()):
            # 409: Video is not ready for revision. (should never be reached)
            raise Conflict("AVEntity not correctly imported: not ready for revision!")

        repo = CreationRepository(self.graph)
        if not repo.is_video_under_revision(item):
            # 409: Video is already under revision.
            raise BadRequest(f"Video [{video.uuid}] is not under revision")
        # ONLY the reviser and the administrator can exit revision
        user = self.get_user()
        iamadmin = self.verify_admin()
        if not iamadmin and not repo.is_revision_assigned_to_user(item, user):
            raise Forbidden(
                f"User [{user.uuid}, {user.name} {user.surname}] cannot exit"
                " revision for video that is not assigned to him/her",
            )

        repo.exit_video_under_revision(item)
        # 204: Video revision successfully exited.
        return self.empty_response()
