# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from commons.logs import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ...auth import authentication
from flask_restful import request
from commons import htmlcodes as hcodes
from commons.services.uuid import getUUID

logger = get_logger(__name__)


#####################################
class Videos(ExtendedApiResource):

    @authentication.authorization_required
    @decorate.apimethod
    def get(self, video_id=None):

        self.graph = self.global_get_service('neo4j')
        data = []

        if video_id is not None:
            v = self.graph.Video.nodes.get(id=video_id)

            video = {}
            video["title"] = v.title
            video["description"] = v.description
            video["duration"] = v.duration
            data.append(video)

        else:

            for v in self.graph.Video.nodes.all():

                video = {}
                video["title"] = v.title
                video["description"] = v.description
                video["duration"] = v.duration
                data.append(video)

        return self.force_response(data)

    @authentication.authorization_required
    @decorate.apimethod
    def post(self, video_id=None):

        self.graph = self.global_get_service('neo4j')

        try:
            data = request.get_json(force=True)
        except:
            data = {}

        logger.critical(data)

        if 'title' not in data:
            return self.force_response(
                errors=[{"Bad Request": "Missing title"}],
                code=hcodes.HTTP_BAD_REQUEST
            )

        if 'description' not in data:
            return self.force_response(
                errors=[{"Bad Request": "Missing description"}],
                code=hcodes.HTTP_BAD_REQUEST
            )

        if 'duration' not in data:
            return self.force_response(
                errors=[{"Bad Request": "Missing duration"}],
                code=hcodes.HTTP_BAD_REQUEST
            )

        video = self.graph.Video()
        video.id = getUUID()
        video.title = data["title"]
        video.description = data["description"]
        video.duration = data["duration"]
        video.save()

        return self.force_response(video.id)
