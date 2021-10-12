"""
Archive management: upload and download files
"""

from imc.endpoints import IMCEndpoint
from restapi import decorators
from restapi.config import DATA_PATH
from restapi.connectors import neo4j
from restapi.exceptions import BadRequest
from restapi.rest.definition import Response
from restapi.services.authentication import User
from restapi.services.download import Downloader
from restapi.services.uploader import Uploader
from restapi.utilities.logs import log


class Upload(Uploader, IMCEndpoint):

    labels = ["file"]

    @decorators.auth.require_all("Archive")
    @decorators.database_transaction
    @decorators.init_chunk_upload
    @decorators.endpoint(
        path="/upload",
        summary="Initialize file upload",
        responses={200: "File upload successfully initialized"},
    )
    def post(
        self, name: str, mimeType: str, size: int, lastModified: int, user: User
    ) -> Response:

        self.graph = neo4j.get_instance()

        group = user.belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = DATA_PATH.joinpath(group.uuid)
        if not upload_dir.exists():
            upload_dir.mkdir()

        return self.init_chunk_upload(upload_dir, name, force=True)

    @decorators.auth.require_all("Archive")
    @decorators.database_transaction
    @decorators.endpoint(
        path="/upload/<filename>",
        summary="Upload a file into the stage area",
        responses={200: "File successfully uploaded"},
    )
    def put(self, filename: str, user: User) -> Response:

        self.graph = neo4j.get_instance()

        group = user.belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = DATA_PATH.joinpath(group.uuid)
        if not upload_dir.exists():
            upload_dir.mkdir()

        completed, upload_response = self.chunk_upload(upload_dir, filename)

        return upload_response

    @decorators.auth.require_all("Archive")
    @decorators.database_transaction
    @decorators.endpoint(
        path="/download/<filename>",
        summary="Download a file",
        responses={
            200: "File successfully downloaded",
            404: "The uploaded content does not exists",
        },
    )
    def get(self, filename: str, user: User) -> Response:
        log.info("get stage content for filename {}", filename)

        self.graph = neo4j.get_instance()

        group = user.belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = DATA_PATH.joinpath(group.uuid)
        return Downloader.download(filename, subfolder=upload_dir)
