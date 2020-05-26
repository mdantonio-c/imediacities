# -*- coding: utf-8 -*-

"""
Upload a file
"""

import os
from flask import send_file, make_response
from mimetypes import MimeTypes

from restapi import decorators
from restapi.utilities.logs import log
from restapi.utilities.htmlcodes import hcodes
from restapi.services.uploader import Uploader
from restapi.exceptions import RestApiException
from restapi.connectors.neo4j import graph_transactions
from imc.apis import IMCEndpoint

mime = MimeTypes()


class Upload(Uploader, IMCEndpoint):

    labels = ['file']
    _GET = {'/download/<filename>': {'summary': 'Download an uploaded file', 'responses': {'200': {'description': 'File successfully downloaded'}, '401': {'description': 'This endpoint requires a valid authorization token'}, '404': {'description': 'The uploaded content does not exists.'}}}}
    _POST = {'/upload': {'summary': 'Initialize file upload', 'responses': {'200': {'description': 'File upload successfully initialized'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}
    _PUT = {'/upload/<filename>': {'summary': 'Upload a file into the stage area', 'responses': {'200': {'description': 'File successfully uploaded'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Archive'])
    def post(self):

        data = self.get_input()
        filename = data.get("name")

        self.graph = self.get_service_instance('neo4j')

        group = self.graph.getSingleLinkedNode(self.get_current_user().belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user", status_code=hcodes.HTTP_BAD_REQUEST
            )

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)

        return self.init_chunk_upload(upload_dir, filename, force=True)

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Archive'])
    def put(self, filename):

        self.graph = self.get_service_instance('neo4j')
        group = self.graph.getSingleLinkedNode(self.get_current_user().belongs_to)

        if group is None:
            raise RestApiException(
                "No group defined for this user", status_code=hcodes.HTTP_BAD_REQUEST
            )

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)

        completed, upload_response = self.chunk_upload(upload_dir, filename)

        return upload_response

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Archive'])
    def get(self, filename):
        log.info("get stage content for filename {}", filename)
        if filename is None:
            raise RestApiException(
                "Please specify a stage filename", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance('neo4j')

        group = self.graph.getSingleLinkedNode(self.get_current_user().belongs_to)

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
                return self.response(errors=["Upload dir not found"])

        staged_file = os.path.join(upload_dir, filename)
        if not os.path.isfile(staged_file):
            raise RestApiException(
                "File not found. Please specify a valid staged file",
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )

        mime_type = mime.guess_type(filename)
        log.debug('mime type: {}', mime_type)

        response = make_response(send_file(staged_file))
        response.headers['Content-Type'] = mime_type[0]
        return response
