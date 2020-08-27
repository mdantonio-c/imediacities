"""
Handle your video metadata
"""
from flask import send_file
from imc.endpoints import IMCEndpoint
from restapi import decorators
from restapi.confs import get_backend_url
from restapi.exceptions import RestApiException
from restapi.models import fields, validate
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


#####################################
class Shots(IMCEndpoint):

    labels = ["shot"]

    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {
            "content_type": fields.Str(
                required=False,
                data_key="content",
                validate=validate.OneOf(["thumbnail"]),
            )
        },
        locations=["query"],
    )
    @decorators.endpoint(
        path="/shots/<shot_id>",
        summary="Gets information about a shot",
        description="Returns a single shot for its id",
        responses={
            200: "Shot information successfully retrieved",
            404: "The video does not exists.",
        },
    )
    def get(self, shot_id, content_type=None):
        """
        Get shot by id.
        """
        log.debug("getting Shot id: {}", shot_id)

        self.graph = self.get_service_instance("neo4j")

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
            return send_file(thumbnail_uri, mimetype="image/jpeg")

        api_url = get_backend_url()
        shot = self.getJsonResponse(node)
        shot["links"]["self"] = api_url + "/api/shots/" + node.uuid
        shot["links"]["thumbnail"] = (
            api_url + "/api/shots/" + node.uuid + "?content=thumbnail"
        )

        return self.response(shot)


class ShotAnnotations(IMCEndpoint):
    """
        Get all shot annotations for a given shot.
    """

    labels = ["shot_annotations"]

    @decorators.auth.require()
    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(
        {
            "anno_type": fields.Str(
                required=False,
                data_key="type",
                description="Filter by annotation type (e.g. TAG)",
                validate=validate.OneOf(["TAG", "DSC"]),
            )
        },
        locations=["query"],
    )
    @decorators.endpoint(
        path="/shots/<shot_id>/annotations",
        summary="Gets shot annotations.",
        description="Returns all the annotations targeting the given shot.",
        responses={200: "List of annotations.", 404: "Shot does not exist."},
    )
    def get(self, shot_id, anno_type=None):
        log.info("get annotations for Shot id: {}", shot_id)

        self.graph = self.get_service_instance("neo4j")

        shot = self.graph.Shot.nodes.get_or_none(uuid=shot_id)

        if not shot:
            log.debug("Shot with uuid {} does not exist", shot_id)
            raise RestApiException(
                "Please specify a valid shot id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_user()

        data = []
        for a in shot.annotation:
            if anno_type is not None and a.annotation_type != anno_type:
                continue
            if a.private:
                if a.creator is None:
                    log.warning(
                        "Invalid state: missing creator for private " "note [UUID:{}]",
                        a.uuid,
                    )
                    continue
                creator = a.creator.single()
                if creator.uuid != user.uuid:
                    continue
            res = self.getJsonResponse(a, max_relationship_depth=0)
            if a.annotation_type in ("TAG", "DSC") and a.creator is not None:
                res["creator"] = self.getJsonResponse(
                    a.creator.single(), max_relationship_depth=0
                )
            # attach bodies
            res["bodies"] = []
            for b in a.bodies.all():
                anno_body = b.downcast()
                body = self.getJsonResponse(anno_body, max_relationship_depth=0)
                res["bodies"].append(body)
            data.append(res)

        return self.response(data)
