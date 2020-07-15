"""
Handle your video entity
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
class Videos(IMCEndpoint):

    """
    Get an AVEntity if its id is passed as an argument.
    Else return all AVEntities in the repository.
    """

    labels = ["video"]
    _GET = {
        "/videos/<video_id>": {
            "summary": "List of videos",
            "description": "Returns a list containing all videos. The list supports paging.",
            "tags": ["videos", "admin"],
            "responses": {
                "200": {"description": "List of videos successfully retrieved"},
                "404": {"description": "The video does not exists."},
            },
        },
        "/videos": {
            "summary": "List of videos",
            "description": "Returns a list containing all videos. The list supports paging.",
            "tags": ["videos", "admin"],
            "responses": {
                "200": {"description": "List of videos successfully retrieved"},
                "404": {"description": "The video does not exists."},
            },
        },
    }
    _POST = {
        "/videos": {
            "summary": "Create a new video description",
            "description": "Simple method to attach descriptive metadata to a previously uploaded video (item).",
            "responses": {
                "200": {"description": "Video description successfully created"}
            },
        }
    }
    _DELETE = {
        "/videos/<video_id>": {
            "summary": "Delete a video description",
            "responses": {"200": {"description": "Video successfully deleted"}},
        }
    }

    @decorators.catch_graph_exceptions
    def get(self, video_id=None):

        if video_id is None and not self.verify_admin():
            raise RestApiException(
                "You are not authorized", status_code=hcodes.HTTP_BAD_FORBIDDEN
            )

        log.debug("getting AVEntity id: {}", video_id)
        self.graph = self.get_service_instance("neo4j")
        data = []

        if video_id is not None:
            # check if the video exists
            try:
                v = self.graph.AVEntity.nodes.get(uuid=video_id)
            except self.graph.AVEntity.DoesNotExist:
                log.debug("AVEntity with uuid {} does not exist", video_id)
                raise RestApiException(
                    "Please specify a valid video id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND,
                )
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

    """
    Create a new video description.
    """

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required()
    def post(self):
        self.graph = self.get_service_instance("neo4j")

        v = self.get_input()
        if len(v) == 0:
            raise RestApiException("Empty input", status_code=hcodes.HTTP_BAD_REQUEST)

        data = self.get_input()

        log.info(data)

        return self.empty_response()

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=["admin_root"])
    def delete(self, video_id):
        """
        Delete existing video description.
        """
        log.debug("deleting AVEntity id: {}", video_id)
        self.graph = self.get_service_instance("neo4j")

        if video_id is None:
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_REQUEST
            )
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
            repo = CreationRepository(self.graph)
            repo.delete_av_entity(v)
            return self.empty_response()
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )


class VideoItem(IMCEndpoint):

    _PUT = {
        "/videos/<video_id>/item": {
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
                "404": {"description": "Video does not exist."},
            },
        }
    }

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=["Archive", "admin_root"], required_roles="any")
    def put(self, video_id):
        """
        Allow user to update item information.
        """
        log.debug("Update Item for AVEntity uuid: {}", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id", status_code=hcodes.HTTP_BAD_REQUEST
            )
        self.graph = self.get_service_instance("neo4j")
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        item = v.item.single()
        if item is None:
            raise RestApiException(
                "This AVEntity may not have been correctly imported. "
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
        log.debug("Item successfully updated for AVEntity uuid {}. {}", video_id, item)

        # 204: Item successfully updated.
        return self.empty_response()


class VideoAnnotations(IMCEndpoint):
    """
        Get all video annotations for a given video.
    """

    labels = ["video_annotations"]
    _GET = {
        "/videos/<video_id>/annotations": {
            "summary": "Gets video annotations",
            "description": "Returns all the annotations targeting the given video item.",
            "responses": {
                "200": {"description": "An annotation object."},
                "404": {"description": "Video does not exist."},
            },
        }
    }

    @decorators.catch_graph_exceptions
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
        locations=["query"],
    )
    @decorators.auth.required()
    def get(self, video_id, anno_type=None, is_manual=False):
        log.debug("get annotations for AVEntity id: {}", video_id)

        self.graph = self.get_service_instance("neo4j")
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

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
    _GET = {
        "/videos/<video_id>/shots": {
            "summary": "Gets video shots",
            "description": "Returns a list of shots belonging to the given video item.",
            "responses": {
                "200": {"description": "An list of shots."},
                "404": {"description": "Video does not exist."},
            },
        }
    }

    @decorators.catch_graph_exceptions
    def get(self, video_id):
        log.debug("get shots for AVEntity id: {}", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance("neo4j")
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_user_if_logged()

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
    _GET = {
        "/videos/<video_id>/segments/<segment_id>": {
            "summary": "Gets all manual segments for a video.",
            "description": "Returns a list of the manual segments belonging to the given video item.",
            "responses": {
                "200": {"description": "An list of manual segments."},
                "404": {"description": "Video does not exist."},
            },
        },
        "/videos/<video_id>/segments": {
            "summary": "Gets all manual segments for a video.",
            "description": "Returns a list of the manual segments belonging to the given video item.",
            "responses": {
                "200": {"description": "An list of manual segments."},
                "404": {"description": "Video does not exist."},
            },
        },
    }
    _PUT = {
        "/videos/<video_id>/segments/<segment_id>": {
            "summary": "Updates a manual video segment",
            "description": "Update a manual video segment identified by uuid",
            "parameters": [
                {
                    "name": "updated_segment",
                    "in": "body",
                    "description": "The manual video segment to update.",
                    "schema": {
                        "required": ["start_frame_idx", "end_frame_idx"],
                        "properties": {
                            "start_frame_idx": {
                                "type": "integer",
                                "format": "int32",
                                "minimum": 0,
                            },
                            "end_frame_idx": {"type": "integer", "format": "int32"},
                        },
                    },
                }
            ],
            "responses": {
                "204": {"description": "Manual video segment successfully updated."},
                "403": {"description": "Operation forbidden."},
                "404": {"description": "Manual video segment does not exist."},
            },
        }
    }
    _DELETE = {
        "/videos/<video_id>/segments/<segment_id>": {
            "summary": "Delete a video segment.",
            "responses": {
                "200": {"description": "Video segment successfully deleted"},
                "404": {"description": "Video segment does not exist"},
            },
        }
    }

    @decorators.catch_graph_exceptions
    @decorators.auth.required()
    def get(self, video_id, segment_id):
        if segment_id is not None:
            log.debug(
                "get manual segment [uuid:{}] for AVEntity [uuid:{}]",
                segment_id,
                video_id,
            )
        else:
            log.debug("get all manual segments for AVEntity [uuid:{}]", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance("neo4j")
        data = []

        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        # user = self.get_user()

        item = video.item.single()
        log.debug("get manual segments for Item [{}]", item.uuid)

        # TODO

        return self.response(data)

    @decorators.catch_graph_exceptions
    @decorators.auth.required()
    def delete(self, video_id, segment_id):
        log.debug(
            "delete manual segment [uuid:{sid}] for AVEntity " "[uuid:{vid}]",
            vid=video_id,
            sid=segment_id,
        )
        raise RestApiException(
            "Delete operation not yet implemented",
            status_code=hcodes.HTTP_NOT_IMPLEMENTED,
        )

    @decorators.catch_graph_exceptions
    @decorators.auth.required()
    def put(self, video_id, segment_id):
        log.debug(
            "update manual segment [uuid:{sid}] for AVEntity " "[uuid:{vid}]",
            vid=video_id,
            sid=segment_id,
        )
        raise RestApiException(
            "Update operation not yet implemented",
            status_code=hcodes.HTTP_NOT_IMPLEMENTED,
        )


class VideoContent(IMCEndpoint, Downloader):

    labels = ["video"]
    _GET = {
        "/videos/<video_id>/content": {
            "summary": "Gets the video content",
            "tags": ["video"],
            "responses": {
                "200": {"description": "Video content successfully retrieved"},
                "404": {"description": "The video content does not exists."},
            },
        }
    }
    _HEAD = {
        "/videos/<video_id>/content": {
            "summary": "Check for video existence",
            "responses": {
                "200": {"description": "The video content exists."},
                "404": {"description": "The video content does not exists."},
            },
        }
    }

    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {
            "content_type": fields.Str(
                required=True,
                data_key="type",
                description="content type (e.g. video, thumbnail, summary)",
                validate=validate.OneOf(["video", "orf", "thumbnail", "summary"]),
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
    def get(self, video_id, content_type, thumbnail_size=None):
        """
        Gets video content such as video strem and thumbnail
        """
        log.debug("get video content for id {}", video_id)

        self.graph = self.get_service_instance("neo4j")
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

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
                raise RestApiException(
                    "Video not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            # all videos are converted to mp4

            filename = os.path.basename(video_uri)
            folder = os.path.dirname(video_uri)
            # return self.send_file_partial(video_uri, mime)
            return self.download(filename=filename, subfolder=folder, mime="video/mp4")

        if content_type == "orf":
            # orf_uri = os.path.dirname(item.uri) + '/transcoded_orf.mp4'
            if item.uri is None:
                raise RestApiException(
                    "Video ORF not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )

            folder = os.path.dirname(item.uri)
            filename = "orf.mp4"
            # orf_uri = os.path.dirname(item.uri) + '/orf.mp4'
            # if orf_uri is None or not os.path.exists(orf_uri):
            if not os.path.exists(os.path.join(folder, filename)):
                raise RestApiException(
                    "Video ORF not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )

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
                raise RestApiException(
                    "Thumbnail not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            return send_file(thumbnail_uri, mimetype="image/jpeg")

        if content_type == "summary":
            summary_uri = item.summary
            log.debug("summary content uri: {}", summary_uri)
            if summary_uri is None:
                raise RestApiException(
                    "Summary not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            return send_file(summary_uri, mimetype="image/jpeg")

        # it should never be reached
        raise RestApiException(
            f"Invalid content type: {content_type}",
            status_code=hcodes.HTTP_NOT_IMPLEMENTED,
        )

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.use_kwargs(
        {
            "content_type": fields.Str(
                required=True,
                data_key="type",
                description="content type (e.g. video, thumbnail, summary)",
                validate=validate.OneOf(["video", "orf", "thumbnail", "summary"]),
            )
        },
        locations=["query"],
    )
    def head(self, video_id, content_type):
        """
        Check for video content existance.
        """
        log.debug("check for video content existence with id {}", video_id)

        self.graph = self.get_service_instance("neo4j")
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        item = video.item.single()
        headers = {}
        if content_type == "video":
            if item.uri is None or not os.path.exists(item.uri):
                raise RestApiException(
                    "Video not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            headers["Content-Type"] = "video/mp4"
        elif content_type == "orf":
            orf_uri = os.path.dirname(item.uri) + "/orf.mp4"
            log.debug(orf_uri)
            if item.uri is None or not os.path.exists(orf_uri):
                raise RestApiException(
                    "Video ORF not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            headers["Content-Type"] = "video/mp4"
        elif content_type == "thumbnail":
            if item.thumbnail is None or not os.path.exists(item.thumbnail):
                raise RestApiException(
                    "Thumbnail not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            headers["Content-Type"] = "image/jpeg"
        elif content_type == "summary":
            if item.summary is None or not os.path.exists(item.summary):
                raise RestApiException(
                    "Summary not found", status_code=hcodes.HTTP_BAD_NOTFOUND
                )
            headers["Content-Type"] = "image/jpeg"
        else:
            # it should never be reached
            raise RestApiException(
                f"Invalid content type: {content_type}",
                status_code=hcodes.HTTP_NOT_IMPLEMENTED,
            )
        return self.response([], headers=headers)


class VideoTools(IMCEndpoint):

    __available_tools__ = ("object-detection", "building-recognition")

    labels = ["video_tools"]
    _POST = {
        "/videos/<video_id>/tools": {
            "summary": "Allow to launch the execution of some video tools.",
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
                "404": {"description": "Video not found."},
                "409": {
                    "description": "Invalid state. E.g. object detection results cannot be imported twice."
                },
            },
        }
    }

    @decorators.catch_graph_exceptions
    @decorators.auth.required(roles=["admin_root"])
    def post(self, video_id):

        log.debug("launch automatic tool for video id: {}", video_id)

        if video_id is None:
            raise RestApiException(
                "Please specify a video id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance("neo4j")
        video = None
        try:
            video = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        item = video.item.single()
        if item is None:
            raise RestApiException(
                "Item not available. Execute the pipeline first!",
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )
        if item.item_type != "Video":
            raise RestApiException(
                "Content item is not a video. Use a valid video id",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )

        params = self.get_input()
        if "tool" not in params:
            raise RestApiException(
                "Please specify the tool to be launched",
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
                    f"No more automatic object detection tags for video {video_id}. Deleted {deleted}",
                    code=hcodes.HTTP_OK_BASIC,
                )
            # DO NOT re-import object detection twice for the same video!
            if repo.check_automatic_od(item.uuid):
                raise RestApiException(
                    "Object detection CANNOT be import twice for the same video.",
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
                    "There are no more automatic building recognition tags for video {}. Deleted {}".format(
                        video_id, deleted
                    ),
                    code=hcodes.HTTP_OK_BASIC,
                )
            # DO NOT re-import building recognition twice for the same video!
            if repo.check_automatic_br(item.uuid):
                raise RestApiException(
                    "Building recognition CANNOT be import twice for the same video.",
                    status_code=hcodes.HTTP_BAD_CONFLICT,
                )
        else:
            # should never be reached
            raise RestApiException(
                f"Specified tool '{tool}' NOT implemented",
                status_code=hcodes.HTTP_NOT_IMPLEMENTED,
            )

        celery = self.get_service_instance("celery")
        task = celery.launch_tool.apply_async(args=[tool, item.uuid], countdown=10)

        return self.response(task.id, code=hcodes.HTTP_OK_ACCEPTED)


class VideoShotRevision(IMCEndpoint):
    """Shot revision endpoint"""

    labels = ["video_shot_revision"]
    _GET = {
        "/videos-under-revision": {
            "summary": "List of videos under revision.",
            "description": "Returns a list containing all videos under revision together with the assignee. The list supports paging.",
            "responses": {
                "200": {
                    "description": "List of videos under revision successfully retrieved",
                    "schema": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/VideoInRevision"},
                    },
                }
            },
        }
    }
    _POST = {
        "/videos/<video_id>/shot-revision": {
            "summary": "Launch the execution of the shot revision tool.",
            "parameters": [
                {
                    "name": "revision",
                    "in": "body",
                    "description": "The new list of cut.",
                    "schema": {"$ref": "#/definitions/ShotRevision"},
                }
            ],
            "responses": {
                "201": {"description": "Execution launched."},
                "403": {"description": "Request forbidden."},
                "404": {"description": "Video not found."},
                "409": {"description": "Invalid state for the video."},
            },
        }
    }
    _PUT = {
        "/videos/<video_id>/shot-revision": {
            "summary": "Put a video under revision",
            "parameters": [
                {
                    "name": "revision",
                    "in": "body",
                    "description": "The revision request.",
                    "schema": {
                        "properties": {
                            "assignee": {
                                "description": "The assignee for the revision (user uuid with Reviser role).",
                                "type": "string",
                            }
                        }
                    },
                }
            ],
            "responses": {
                "204": {"description": "Video under revision successfully."},
                "400": {"description": "Assignee not valid."},
                "409": {
                    "description": "Video is already under revision or it is not ready for revision."
                },
                "403": {"description": "Operation forbidden."},
                "404": {"description": "Video does not exist."},
            },
        }
    }
    _DELETE = {
        "/videos/<video_id>/shot-revision": {
            "summary": "Take off revision from a video.",
            "responses": {
                "204": {"description": "Video revision successfully exited."},
                "403": {"description": "Request forbidden."},
                "404": {"description": "Video not found."},
            },
        }
    }

    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {
            "input_assignee": fields.Str(
                required=False,
                data_key="assignee",
                description="Assignee's uuid of the revision",
            )
        },
        locations=["query"],
    )
    @decorators.auth.required(roles=["Reviser", "admin_root"], required_roles="any")
    def get(self, input_assignee=None):
        """Get all videos under revision"""
        log.debug("Getting videos under revision.")
        self.graph = self.get_service_instance("neo4j")
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

    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=["Reviser", "admin_root"], required_roles="any")
    def put(self, video_id):
        """Put a video under revision"""
        log.debug("Put video {0} under revision", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance("neo4j")
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        item = v.item.single()
        if item is None:
            # 409: Video is not ready for revision. (should never be reached)
            raise RestApiException(
                "This AVEntity may not have been correctly imported. "
                "No ready for revision!",
                status_code=hcodes.HTTP_BAD_CONFLICT,
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
        assignee = user
        assignee_is_admin = iamadmin
        # allow admin to pass the assignee
        data = self.get_input()
        if iamadmin and "assignee" in data:
            assignee = self.graph.User.nodes.get_or_none(uuid=data["assignee"])
            if assignee is None:
                # 400: description: Assignee not valid.
                raise RestApiException(
                    "Invalid candidate. User [{uuid}] does not exist".format(
                        uuid=data["assignee"]
                    ),
                    status_code=hcodes.HTTP_BAD_NOTFOUND,
                )
            # is the assignee an admin_root?
            assignee_is_admin = False
            for role in assignee.roles.all():
                if role.name == "admin_root":
                    assignee_is_admin = True
                    break
        log.debug("Assignee is admin? {}", assignee_is_admin)

        repo = CreationRepository(self.graph)

        if not assignee_is_admin and not repo.item_belongs_to_user(item, assignee):
            raise RestApiException(
                "User [{}, {} {}] cannot revise video that does not belong to him/her".format(
                    user.uuid, user.name, user.surname
                ),
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )
        if repo.is_video_under_revision(item):
            # 409: Video is already under revision.
            raise RestApiException(
                f"Video [{v.uuid}] is already under revision",
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )

        repo.move_video_under_revision(item, assignee)
        # 204: Video under revision successfully.
        return self.empty_response()

    @decorators.catch_graph_exceptions
    @decorators.auth.required(roles=["Reviser", "admin_root"], required_roles="any")
    def post(self, video_id):
        """Start a shot revision procedure"""
        log.debug("Start shot revision for video {0}", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id", status_code=hcodes.HTTP_BAD_REQUEST
            )
        self.graph = self.get_service_instance("neo4j")
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        item = v.item.single()
        if item is None:
            # 409: Video is not ready for revision. (should never be reached)
            raise RestApiException(
                "This AVEntity may not have been correctly imported. "
                "No ready for revision!",
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )
        repo = CreationRepository(self.graph)
        # be sure video is under revision
        if not repo.is_video_under_revision(item):
            raise RestApiException(
                f"This video [{video_id}] is not under revision!",
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )
        # ONLY the reviser and the administrator can provide a new list of cuts
        user = self.get_user()
        iamadmin = self.verify_admin()
        if not iamadmin and not repo.is_revision_assigned_to_user(item, user):
            raise RestApiException(
                "User [{}, {} {}] cannot revise video that is not assigned to him/her".format(
                    user.uuid, user.name, user.surname
                ),
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        revision = self.get_input()
        # validate request body
        if "shots" not in revision or not revision["shots"]:
            raise RestApiException(
                "Provide a valid list of cuts", status_code=hcodes.HTTP_BAD_REQUEST
            )
        for idx, s in enumerate(revision["shots"]):
            if "shot_num" not in s:
                raise RestApiException(
                    f"Missing shot_num in shot: {s}",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            if idx > 0 and "cut" not in s:
                raise RestApiException(
                    "Missing cut for shot[{}]".format(s["shot_num"]),
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            if "confirmed" in s and not isinstance(s["confirmed"], bool):
                raise RestApiException(
                    "Invalid confirmed value", status_code=hcodes.HTTP_BAD_REQUEST
                )
            if "double_check" in s and not isinstance(s["double_check"], bool):
                raise RestApiException(
                    "Invalid double_check value", status_code=hcodes.HTTP_BAD_REQUEST
                )
            if "annotations" not in s:
                raise RestApiException(
                    f"Missing annotations in shot: {s}",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
            if (
                "annotations" in s
                and not isinstance(s["annotations"], type(list))
                and not all(isinstance(val, str) for val in s["annotations"])
            ):
                raise RestApiException(
                    "Invalid annotations value. Expected list<str>",
                    status_code=hcodes.HTTP_BAD_REQUEST,
                )
        if "exitRevision" in revision and not isinstance(
            revision["exitRevision"], bool
        ):
            raise RestApiException(
                "Invalid exitRevision", status_code=hcodes.HTTP_BAD_REQUEST
            )

        revision["reviser"] = user.uuid
        # launch asynch task
        try:
            celery = self.get_service_instance("celery")
            task = celery.shot_revision.apply_async(
                args=[revision, item.uuid], countdown=10, priority=5
            )
            assignee = item.revision.single()
            rel = item.revision.relationship(assignee)
            rel.state = "R"
            rel.save()
            # 202: OK_ACCEPTED
            return self.response(task.id, code=hcodes.HTTP_OK_ACCEPTED)
        except BaseException as e:
            raise e

    @decorators.catch_graph_exceptions
    @decorators.auth.required(roles=["Reviser", "admin_root"], required_roles="any")
    def delete(self, video_id):
        """Take off revision from a video"""
        log.debug("Exit revision for video {0}", video_id)
        if video_id is None:
            raise RestApiException(
                "Please specify a video id", status_code=hcodes.HTTP_BAD_REQUEST
            )
        self.graph = self.get_service_instance("neo4j")
        try:
            v = self.graph.AVEntity.nodes.get(uuid=video_id)
        except self.graph.AVEntity.DoesNotExist:
            log.debug("AVEntity with uuid {} does not exist", video_id)
            raise RestApiException(
                "Please specify a valid video id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        item = v.item.single()
        if item is None:
            # 409: Video is not ready for revision. (should never be reached)
            raise RestApiException(
                "This AVEntity may not have been correctly imported. "
                "No ready for revision!",
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )

        repo = CreationRepository(self.graph)
        if not repo.is_video_under_revision(item):
            # 409: Video is already under revision.
            raise RestApiException(
                f"Video [{v.uuid}] is not under revision",
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        # ONLY the reviser and the administrator can exit revision
        user = self.get_user()
        iamadmin = self.verify_admin()
        if not iamadmin and not repo.is_revision_assigned_to_user(item, user):
            raise RestApiException(
                "User [{}, {} {}] cannot exit revision for video that is "
                "not assigned to him/her".format(user.uuid, user.name, user.surname),
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        repo.exit_video_under_revision(item)
        # 204: Video revision successfully exited.
        return self.empty_response()
