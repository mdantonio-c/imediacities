"""
Upload a file
"""

import os
from mimetypes import MimeTypes

from flask import make_response, send_file
from imc.endpoints import IMCEndpoint
from restapi import decorators
from restapi.connectors import neo4j
from restapi.exceptions import BadRequest, NotFound
from restapi.services.uploader import Uploader
from restapi.utilities.logs import log

mime = MimeTypes()


class Upload(Uploader, IMCEndpoint):

    labels = ["file"]

    @decorators.auth.require_all("Archive")
    @decorators.graph_transactions
    @decorators.init_chunk_upload
    @decorators.endpoint(
        path="/upload",
        summary="Initialize file upload",
        responses={200: "File upload successfully initialized"},
    )
    def post(self, name, **kwargs):

        self.graph = neo4j.get_instance()

        group = self.get_user().belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)

        return self.init_chunk_upload(upload_dir, name, force=True)

    @decorators.auth.require_all("Archive")
    @decorators.graph_transactions
    @decorators.endpoint(
        path="/upload/<filename>",
        summary="Upload a file into the stage area",
        responses={200: "File successfully uploaded"},
    )
    def put(self, filename):

        self.graph = neo4j.get_instance()
        group = self.get_user().belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)

        completed, upload_response = self.chunk_upload(upload_dir, filename)

        return upload_response

    @decorators.auth.require_all("Archive")
    @decorators.graph_transactions
    @decorators.endpoint(
        path="/download/<filename>",
        summary="Download an uploaded file",
        responses={
            200: "File successfully downloaded",
            404: "The uploaded content does not exists",
        },
    )
    def get(self, filename):
        log.info("get stage content for filename {}", filename)
        if filename is None:
            raise BadRequest("Please specify a stage filename")

        self.graph = neo4j.get_instance()

        group = self.get_user().belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)
            if not os.path.exists(upload_dir):
                raise NotFound("Upload dir not found")

        staged_file = os.path.join(upload_dir, filename)
        if not os.path.isfile(staged_file):
            raise NotFound("File not found. Please specify a valid staged file")

        mime_type = mime.guess_type(filename)
        log.debug("mime type: {}", mime_type)

        response = make_response(send_file(staged_file))
        response.headers["Content-Type"] = mime_type[0]
        return response
