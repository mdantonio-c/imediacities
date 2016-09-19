# -*- coding: utf-8 -*-

"""
An endpoint example
"""

from commons.logs import get_logger
from ..base import ExtendedApiResource
from .. import decorators as decorate
from ...auth import authentication

logger = get_logger(__name__)


#####################################
class Videos(ExtendedApiResource):

    @authentication.authorization_required
    @decorate.apimethod
    def get(self, video_id=None):

        self.graph = self.global_get_service('neo4j')

        data = []

        video = {}
        video["title"] = "Test"
        video["description"] = "This is a description test"
        data.append(video)

        video = {}
        video["title"] = "Test2"
        video["description"] = "This is a second description test"
        data.append(video)

        return self.force_response(data)
