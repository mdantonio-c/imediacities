# -*- coding: utf-8 -*-

"""
Upload a file
"""

import os
from flask import send_file, make_response
from mimetypes import MimeTypes

from restapi import decorators as decorate
from restapi.protocols.bearer import authentication
from restapi.utilities.logs import get_logger
from restapi.utilities.htmlcodes import hcodes
from restapi.services.uploader import Uploader
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
from restapi.flask_ext.flask_neo4j import graph_transactions
from restapi.decorators import catch_graph_exceptions

log = get_logger(__name__)
mime = MimeTypes()


class Upload(Uploader, GraphBaseOperations):

    labels = ['file']
    GET = {'/download/<filename>': {'summary': 'Download an uploaded file', 'responses': {'200': {'description': 'File successfully downloaded'}, '401': {'description': 'This endpoint requires a valid authorization token'}, '404': {'description': 'The uploaded content does not exists.'}}}}
    POST = {'/upload/<filename>': {'summary': 'Upload a file into the stage area', 'responses': {'200': {'description': 'File successfully uploaded'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    @authentication.required(roles=['Archive'])
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
    @authentication.required(roles=['Archive'])
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
