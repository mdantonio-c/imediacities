"""
List content from upload dir and import of data and metadata
"""
import os
from typing import Any, Dict

from imc.endpoints import IMCEndpoint
from imc.tasks.services.efg_xmlparser import EFG_XMLParser
from restapi import decorators
from restapi.connectors import celery, neo4j
from restapi.exceptions import BadRequest, Conflict, NotFound, ServerError
from restapi.models import fields, validate
from restapi.services.authentication import Role
from restapi.utilities.logs import log


#####################################
class Stage(IMCEndpoint):

    labels = ["file"]

    @staticmethod
    def getType(filename):
        name, file_extension = os.path.splitext(filename)

        if file_extension is None:
            return "unknown"

        metadata_exts = [".xml", ".xls"]
        if file_extension in metadata_exts:
            return "metadata"

        video_exts = [".mp4", ".ts", ".mpg", ".mpeg", ".mkv"]
        if file_extension in video_exts:
            return "video"

        audio_exts = [".aac", ".mp2", ".mp3", ".wav"]
        if file_extension in audio_exts:
            return "audio"

        image_exts = [".tif", ".jpg", ".tiff", ".jpeg"]
        if file_extension in image_exts:
            return "image"

        text_exts = [".pdf", ".doc", ".docx"]
        if file_extension in text_exts:
            return "text"

        return "unknown"

    def lookup_content(self, path, source_id):
        """
        Look for a filename in the form of:
        ARCHIVE_SOURCEID.[extension]
        """
        content_filename = None
        files = [f for f in os.listdir(path) if not f.endswith(".xml")]
        for f in files:
            tokens = os.path.splitext(f)[0].split("_")
            if len(tokens) == 0:
                continue
            if tokens[-1] == source_id:
                log.info("Content file FOUND: {0}", f)
                # content_path = os.path.join(path, f)
                content_filename = f
                break
        return content_filename

    def extract_creation_ref(self, path):
        """
        Extract the source id reference from the XML file
        """
        parser = EFG_XMLParser()
        return parser.get_creation_ref(path)

    @decorators.auth.require_any(
        Role.ADMIN, Role.USER, "Archive", "Reviser", "Researcher"
    )
    @decorators.get_pagination
    @decorators.endpoint(
        path="/stage",
        summary="List of files contained in the stage area of the specified group",
        responses={200: "List of files and directories successfully retrieved"},
    )
    @decorators.endpoint(
        path="/stage/<group>",
        summary="List of files contained in the stage area of the specified group",
        responses={200: "List of files and directories successfully retrieved"},
    )
    def get(self, get_total, page, size, sort_by, sort_order, input_filter, group=None):
        self.graph = neo4j.get_instance()

        if not self.verify_admin():
            # Only admins can specify a different group to be inspected
            group = None

        if group is None:
            user = self.get_user()
            if user is None:  # pragma: no cover
                raise BadRequest("No user defined")

            group = user.belongs_to.single()
        else:
            group = self.graph.Group.nodes.get_or_none(uuid=group)

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            os.mkdir(upload_dir)
            if not os.path.exists(upload_dir):
                raise ServerError("Upload dir not found")

        dirs = os.listdir(upload_dir)

        if input_filter:
            filtered_dirs = []
            for f in dirs:
                if input_filter in f.lower():
                    filtered_dirs.append(f)

            dirs = filtered_dirs

        if get_total:
            return {"total": len(dirs)}

        if sort_by:

            if sort_by == "name":
                sort_fn = SortFunctions.sort_by_name
            elif sort_by == "type":
                sort_fn = SortFunctions.sort_by_type
            # elif sort_by == "size":
            #     sort_fn = SortFunctions.sort_by_size
            # elif sort_by == "creation":
            #     sort_fn = SortFunctions.sort_by_creation
            # elif sort_by == "status":
            #     sort_fn = SortFunctions.sort_by_status
            else:
                raise BadRequest(f"Unknown sort request: {sort_by}")

            dirs = sorted(dirs, key=sort_fn, reverse=sort_order == "desc")

        offset = (page - 1) * size

        counter = 0
        data = []
        for f in dirs:

            path = os.path.join(upload_dir, f)
            if not os.path.isfile(path):
                continue

            if f[0] == ".":
                continue

            counter += 1

            if offset >= counter:
                continue

            if offset + size < counter:
                break

            stat = os.stat(path)

            row: Dict[str, Any] = {}
            row["name"] = f
            row["size"] = stat.st_size
            row["creation"] = stat.st_ctime
            row["modification"] = stat.st_mtime
            row["type"] = self.getType(f)
            row["status"] = "-"
            res = self.graph.Stage.nodes.get_or_none(filename=f)
            if res is not None:
                row["status"] = res.status
                row["status_message"] = res.status_message
                row["task_id"] = res.task_id
                row["warnings"] = res.warnings
                # cast down to Meta or Content stage
                subres = res.downcast()
                if "MetaStage" in subres.labels():
                    item = subres.item.single()
                    # add binding info ONLY for processed record
                    if item is not None:
                        binding = {}
                        source_id = None
                        creation = item.creation.single()
                        if creation is not None:
                            sources = creation.record_sources.all()
                            source_id = sources[0].source_id
                            binding["source_id"] = source_id
                        content_stage = item.content_source.single()
                        if content_stage is not None:
                            binding["filename"] = content_stage.filename
                            binding["status"] = content_stage.status
                        else:
                            binding["filename"] = self.lookup_content(
                                upload_dir, source_id
                            )
                            binding["status"] = "PENDING"
                        row["binding"] = binding

            data.append(row)

        return self.response(data)

    @decorators.auth.require_any(
        Role.ADMIN, Role.USER, "Archive", "Reviser", "Researcher"
    )
    @decorators.use_kwargs(
        {
            "filename": fields.Str(
                required=True,
                description="The metadata file to be imported",
            ),
            "mode": fields.Str(
                missing="fast",
                description="Different modes for pipeline execution",
                validate=validate.OneOf(["fast", "clean", "skip"]),
            ),
            "update": fields.Bool(
                missing=True,
                description="only for metadata update",
            ),
            "force_reprocessing": fields.Bool(
                missing=False,
                description="Allow to force re-processing of COMPLETED contents",
            ),
        }
    )
    @decorators.endpoint(
        path="/stage",
        summary="Import a file from the stage area",
        responses={
            200: "File successfully imported",
            409: "No source id found in metadata file.",
        },
    )
    def post(self, filename, mode, update, force_reprocessing):
        """
        Start IMPORT
        1) estraggo il source id dal file dei metadati
            se non lo trovo -> exception
        2) cerco nel database se esiste già un META_STAGE collegato a quel SOURCE_ID e appartenente al gruppo
            se ne trovo più di uno -> exception
            se ne trovo uno -> updating metadata
                se il nome del file dei metadati è diverso da quello in db -> exception
                cerco se c'è un content stage associato a quel meta stage
                    se esiste e se ha status COMPLETED -> mode=skip
            se ne trovo zero -> creating new element
                se il file dei metadati non rispetta la convenzione del name '<archive code>_<source id>.xml'
                    cambio il nome al file
                cerco se esiste già un metastage con quel filename
                    se non esiste lo creo
        3) faccio partire l'import con parametri: path, meta_stage.uuid, mode, metadata_update
        """

        self.graph = neo4j.get_instance()
        celery_ext = celery.get_instance()

        user = self.get_user()
        if user is None:  # pragma: no cover
            raise BadRequest("No user defined")

        group = user.belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise BadRequest("Upload dir not found")

        path = os.path.join(upload_dir, filename)
        if not os.path.isfile(path):
            raise BadRequest(f"File not found: {filename}")

        # 1) estraggo il source id dal file dei metadati
        log.debug("Extracting source id from metadata file {}", filename)
        source_id = self.extract_creation_ref(path)
        if source_id is None:
            log.debug("No source ID found in metadata file {}", path)
            raise Conflict(f"No source ID found in metadata file: {filename}")
        log.debug("Source id {} found in metadata file", source_id)

        # 2) cerco nel database se esiste già un META_STAGE collegato a quel SOURCE_ID
        #     e appartenente al gruppo
        meta_stage = None
        try:
            query = "match (g:Group)<-[r4:IS_OWNED_BY]-(ms:MetaStage) \
                        match (ms:MetaStage)<-[r3:META_SOURCE]-(i:Item) \
                        match (i:Item)-[r2:CREATION]->(c:Creation) \
                        match (c:Creation)-[r1:RECORD_SOURCE]-> (rs:RecordSource) \
                        WHERE rs.source_id = '{source_id}' and g.uuid = '{guuid}' \
                        return ms"

            results = self.graph.cypher(
                query.format(source_id=source_id, guuid=group.uuid)
            )
            c = [self.graph.MetaStage.inflate(row[0]) for row in results]
            if len(c) > 1:
                # there are more than one MetaStage related to the same source id: Database incoherence!
                log.error(
                    "Database incoherence: there are more than one MetaStage related to the same source id {}",
                    source_id,
                )
                raise ServerError(
                    "System incoherent state: it is not possible to perform the import"
                )
            if len(c) == 1:
                # Source id already exists in database: updating metadata
                log.debug("Source ID {} already exists in the database", source_id)
                meta_stage = c[0]
                if meta_stage is not None:
                    dbFilename = meta_stage.filename
                    log.debug("dbFilename={}", dbFilename)
                    if filename != dbFilename:
                        raise Conflict(
                            f"Source ID {source_id} already exists in the database "
                            f"but with different filename {dbFilename}: "
                            "unable to proceed with import",
                        )

                    # cerco se c'è un content stage associato a quel meta stage
                    # per vedere se status COMPLETED
                    query2 = (
                        "MATCH (cs:ContentStage)<-[r1:CONTENT_SOURCE]-(i:Item) "
                        "MATCH (i)-[r2:META_SOURCE]-> (ms:MetaStage) "
                        "WHERE ms.uuid='{uuid}' "
                        "RETURN cs"
                    )
                    results2 = self.graph.cypher(query2.format(uuid=meta_stage.uuid))
                    c2 = [self.graph.ContentStage.inflate(row[0]) for row in results2]
                    if len(c2) == 1:
                        content_stage = c2[0]
                        if (
                            content_stage is not None
                            and content_stage.status == "COMPLETED"
                            and not force_reprocessing
                        ):
                            log.warning(
                                "This content item has already been "
                                "successfully processed. Force SKIP mode."
                            )
                            mode = "skip"
                else:
                    log.debug("meta_stage is null")
                    raise ServerError(
                        "System incoherence error: cannot perform the import"
                    )
            if len(c) == 0:
                # Source id does not exist in the database: creating new element
                log.debug(
                    "Source ID {} does not exist in the database: creating new element",
                    source_id,
                )
                # force filename convention '<archive code>_<source id>.xml'
                standard_filename = group.shortname + "_" + source_id + ".xml"
                if filename != standard_filename:
                    log.debug(
                        "File {} has not standard file name: renaming it to {}",
                        filename,
                        standard_filename,
                    )
                    standard_path = os.path.join(upload_dir, standard_filename)
                    # rename the file in the filesystem
                    try:
                        # cambio il nome al file dell'utente
                        # TODO come faccio ad avvisarlo????
                        os.replace(path, standard_path)
                    except OSError:
                        log.debug(
                            "Error in renaming file {} to {}: ", path, standard_path
                        )
                        raise Conflict(f"System error: cannot rename file {path}")

                    path = standard_path

                # cerco se esiste già un metastage con quel filename altrimenti lo creo
                properties = {"filename": standard_filename, "path": path}
                try:
                    meta_stage = self.graph.MetaStage.nodes.get(**properties)
                    log.debug(
                        "MetaStage already exists for file {}, meta_stage.uuid={}",
                        path,
                        meta_stage.uuid,
                    )
                except self.graph.MetaStage.DoesNotExist:
                    log.debug("MetaStage does not exists for file {}", path)
                    meta_stage = self.graph.MetaStage(**properties).save()
                    meta_stage.ownership.connect(group)
                    log.debug(
                        "MetaStage created for {}, meta_stage.uuid={}",
                        path,
                        meta_stage.uuid,
                    )

            log.debug("Starting import of file path={}", path)
            if meta_stage:
                log.debug("with meta_stage.uuid={}", meta_stage.uuid)
            else:
                log.debug("with meta_stage = None!")
            log.debug("with mode={}", mode)
            log.debug("with metadata_update={}", update)

        except self.graph.MetaStage.DoesNotExist:
            log.debug("MetaStage not exist for source id {}", source_id)

        if not meta_stage:
            raise NotFound(f"MetaStage not exist for source id {source_id}")

        # 3) starting import
        task = celery_ext.celery_app.send_task(
            "import_file", args=[path, meta_stage.uuid, mode, update], countdown=10
        )

        meta_stage.status = "IMPORTING"
        meta_stage.task_id = task.id
        meta_stage.save()

        return self.response(task.id)

    @decorators.auth.require_any(
        Role.ADMIN, Role.USER, "Archive", "Reviser", "Researcher"
    )
    @decorators.endpoint(
        path="/stage/<filename>",
        summary="Delete a file from the stage area",
        responses={200: "File successfully deleted"},
    )
    def delete(self, filename):

        self.graph = neo4j.get_instance()

        user = self.get_user()
        if user is None:  # pragma: no cover
            raise BadRequest("No user defined")

        group = user.belongs_to.single()

        if group is None:
            raise BadRequest("No group defined for this user")

        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise BadRequest("Upload dir not found")

        path = os.path.join(upload_dir, filename)
        if not os.path.isfile(path):
            raise BadRequest(f"File not found: {filename}")

        os.remove(path)
        return self.empty_response()


class SortFunctions:
    @staticmethod
    def sort_by_name(t):
        return t

    @staticmethod
    def sort_by_type(t):
        return Stage.getType(t)

    @staticmethod
    def sort_by_size(t):
        log.warning("Sort by size is not implemented")
        return t

    @staticmethod
    def sort_by_creation(t):
        log.warning("Sort by creation is not implemented")
        return t

    @staticmethod
    def sort_by_status(t):
        log.warning("Sort by status is not implemented")
        return t
