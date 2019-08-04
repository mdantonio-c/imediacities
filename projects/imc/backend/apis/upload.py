# -*- coding: utf-8 -*-

"""
Upload a file
"""

import os
from flask import send_file, make_response
from mimetypes import MimeTypes

from restapi import decorators as decorate
from utilities.logs import get_logger
from utilities import htmlcodes as hcodes
from restapi.services.uploader import Uploader
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions

log = get_logger(__name__)
mime = MimeTypes()


class Upload(Uploader, GraphBaseOperations):
    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self, filename):

        self.graph = self.get_service_instance('neo4j')

        group = self.getSingleLinkedNode(self.get_current_user().belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user", status_code=hcodes.HTTP_BAD_REQUEST
            )

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)

        upload_response = self.upload_data(filename, subfolder=upload_dir, force=False)

        return upload_response

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def get(self, filename):
        log.info("get stage content for filename %s" % filename)
        if filename is None:
            raise RestApiException(
                "Please specify a stage filename", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance('neo4j')

        group = self.getSingleLinkedNode(self.get_current_user().belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user", status_code=hcodes.HTTP_BAD_REQUEST
            )

        if group is None:
            raise RestApiException(
                "No group defined for this user", status_code=hcodes.HTTP_BAD_REQUEST
            )

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)
            if not os.path.exists(upload_dir):
                return self.force_response([], errors=["Upload dir not found"])

        staged_file = os.path.join(upload_dir, filename)
        if not os.path.isfile(staged_file):
            raise RestApiException(
                "File not found. Please specify a valid staged file",
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )

        mime_type = mime.guess_type(filename)
        log.debug('mime type: {}'.format(mime_type))

        response = make_response(send_file(staged_file))
        response.headers['Content-Type'] = mime_type[0]
        return response
