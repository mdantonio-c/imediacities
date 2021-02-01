"""
Bulk endpoint.

The bulk API makes it possible to perform many operations in a single API call.
e.g.
POST api/bulk
{"update": {"guid":"9fea0424-1280-4bba-9be9-d6071ad32354"}}
{"import": {"guid":"9fea0424-1280-4bba-9be9-d6071ad32354", "mode": "skip", "update":true}}
{"delete": {"entity":"AVEntity", "uuids": ["10fe3277-2d25-4de0-8e1d-bdd2a5dd6895", etc.]}}

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

import os
import re
from datetime import datetime

from imc.endpoints import IMCEndpoint
from imc.models import BulkSchema
from imc.tasks.services.creation_repository import CreationRepository
from restapi import decorators
from restapi.connectors import celery, neo4j
from restapi.exceptions import BadRequest, NotFound
from restapi.services.authentication import Role
from restapi.utilities.logs import log


#####################################
class Bulk(IMCEndpoint):

    labels = ["bulk"]

    def lookup_latest_dir(self, path):
        """
        Look for the sub-directory of path in the forms of:
        %Y-%m-%d (example 2018-04-19)
        %Y-%m-%dT%H:%M:%S.%fZ (example 2018-04-19T11:22:12.0Z)
        which name is the most recent date
        """
        log.debug("lookup_latest_dir.input path = {}", path)

        POSSIBLE_FORMATS = ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S.%fZ"]

        found_date = None
        found_dir = None
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        for d in dirs:
            parsed_date = None
            for format in POSSIBLE_FORMATS:
                try:
                    parsed_date = datetime.strptime(d, format)
                    break
                except Exception:
                    # il nome della dir non e' nel formato
                    pass
            if parsed_date is not None:
                # all'inizio found_dir e' vuoto
                if found_date is None:
                    found_date = parsed_date
                    found_dir = d
                    continue
                if parsed_date > found_date:
                    found_date = parsed_date
                    found_dir = d
            else:
                log.warning("cannot parse dir = {}", d)
        return os.path.join(path, found_dir)

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.use_kwargs(BulkSchema)
    @decorators.endpoint(
        path="/bulk",
        summary="Perform many operations such as import, update, delete etc.",
        description="The bulk api makes it possible to perform many operations in a single api call",
        responses={202: "Bulk action successfully accepted", 400: "Bad request."},
    )
    def post(self, **req_action):

        self.graph = neo4j.get_instance()
        c = celery.get_instance()

        if action := req_action.get("update"):
            log.debug("Start bulk procedure...")
            # check group uid
            guid = action.get("guid")
            group = self.graph.Group.nodes.get_or_none(uuid=guid)
            if group is None:
                raise NotFound(f"Group ID {guid} not found")
            log.info("Update procedure for Group '{0}'", group.shortname)
            # check if the parameter 'force_reprocessing' has been specified
            force_reprocessing = action.get("force_reprocessing", False)
            log.debug("force_reprocessing: {}", force_reprocessing)

            # retrieve XML files from delta upload dir
            # (Downloaded with oai-pmh only delta compared to the last harvest.
            #  Take dir= /uploads/<guid>/upload/<date>/ with the most recent date)
            upload_dir = "/uploads/" + group.uuid
            upload_delta_dir = os.path.join(upload_dir, "upload")
            if not os.path.exists(upload_delta_dir):
                raise NotFound("Upload dir not found")

            # inside the upload_delta_dir I have to look for the sub-dir that
            # corresponds to the most recent date
            upload_latest_dir = self.lookup_latest_dir(upload_delta_dir)

            if upload_latest_dir is None:
                log.debug("Upload dir not found")
                raise NotFound("Upload dir not found")

            task = c.celery_app.send_task(
                "bulk_update",
                args=[guid, upload_latest_dir, force_reprocessing],
                countdown=10,
            )
            log.debug("Task id={}", task.id)

        # ##################################################################
        elif action := req_action.get("import_"):
            # check group uid
            guid = action.get("guid")
            group = self.graph.Group.nodes.get_or_none(uuid=guid)
            if group is None:
                raise NotFound(f"Group ID {guid} not found")
            update = action.get("update")
            mode = action.get("mode")
            retry = action.get("retry")
            self._bulk_import(group, mode, update, retry)

        # ##################################################################
        elif action := req_action.get("v2"):
            guid = action.get("guid")
            # check group uid
            group = self.graph.Group.nodes.get_or_none(uuid=guid)
            if group is None:
                raise NotFound(f"Group ID {guid} not found")
            retry = action.get("retry")
            self._bulk_v2(group, retry)

        # ##################################################################
        elif action := req_action.get("delete"):
            entity = action.get("entity")
            if action.get("delete_all"):
                all_query = f"match (n:{entity}) return n.uuid"
                uuids = [row[0] for row in self.graph.cypher(all_query)]
            else:
                uuids = action.get("uuids")
            self._bulk_delete(entity, uuids)
            return self.empty_response()

        else:
            raise BadRequest("Unexpected action request")

        return self.response("Bulk request accepted", code=202)

    def _bulk_import(self, group, mode, update, retry):
        log.info(
            "Import procedure for Group '{}' (mode: {}; update {}; retry {})",
            group.shortname,
            mode,
            update,
            retry,
        )

        # retrieve XML files from upload dir
        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise NotFound("Upload dir not found")

        files = [f for f in os.listdir(upload_dir) if f.endswith(".xml")]
        total_to_be_imported = len(files)
        skipped = 0
        imported = 0
        for f in files:
            path = os.path.join(upload_dir, f)
            filename = f
            properties = {}
            properties["filename"] = filename
            properties["path"] = path

            # ignore previous failures
            if not retry:
                try:
                    # props = {'status': 'ERROR', 'filename': f} #OLD
                    props = {"status": "ERROR", "path": path}
                    self.graph.MetaStage.nodes.get(**props)
                    skipped += 1
                    log.debug("SKIPPED already imported with ERROR. Filename {}", path)
                    continue
                except self.graph.MetaStage.DoesNotExist:
                    pass

            if not update:
                query = "match (n:MetaStage) WHERE n.path = '{path}' \
                                      match (n)-[r1:META_SOURCE]-(i:Item) \
                                      match (i)-[r2:CREATION]->(c:Creation) \
                                      return c"
                results = self.graph.cypher(query.format(path=path))
                c = [self.graph.Creation.inflate(row[0]) for row in results]
                if len(c) == 1:
                    skipped += 1
                    log.debug(
                        "SKIPPED filename: {0}. Creation uuid: {1}", path, c[0].uuid
                    )
                    continue
            log.info("Importing metadata file: {}", path)
            try:
                resource = self.graph.MetaStage.nodes.get(**properties)
                log.debug("Resource already exist for {}", path)
            except self.graph.MetaStage.DoesNotExist:
                resource = self.graph.MetaStage(**properties).save()
                resource.ownership.connect(group)
                log.debug("Metadata Resource created for {}", path)

            task = c.celery_app.send_task(
                "import_file", args=[path, resource.uuid, mode], countdown=10
            )

            resource.status = "IMPORTING"
            resource.task_id = task.id
            resource.save()
            imported += 1

        log.info("------------------------------------")
        log.info("Total record: {}", total_to_be_imported)
        log.info("importing: {}", imported)
        log.info("skipped {}", skipped)
        log.info("------------------------------------")

    def _bulk_v2(self, group, retry):
        log.info("V2 procedure for Group '{}'", group.shortname)

        # retrieve v2_ XML files from upload dir
        upload_dir = os.path.join("/uploads", group.uuid)
        if not os.path.exists(upload_dir):
            raise NotFound("Upload dir not found")

        # v2_ is used for the 'other version' (exclude .xml)
        files = [
            f
            for f in os.listdir(upload_dir)
            if not f.endswith(".xml") and re.match(r"^v2_.*", f, re.I)
        ]
        total_available = len(files)
        if total_available == 0:
            raise NotFound(f"No v2 content for group {group.shortname}")
        log.info("Total v2 files currently available: {}", total_available)
        skipped = 0
        imported = 0
        warnings = 0
        for f in files:
            # cut away prefix and look for the related content
            origin = f.split("_", 1)[1]
            source_path = os.path.join(upload_dir, origin)
            query = (
                "MATCH (n:ContentStage {{path:'{path}', status:'COMPLETED'}})"
                "<-[:CONTENT_SOURCE]-(i:Item) RETURN i".format(path=source_path)
            )
            results = self.graph.cypher(query)
            c = [self.graph.Item.inflate(row[0]) for row in results]
            if len(c) == 0:
                log.warning(
                    "Cannot load {v2} because origin content does "
                    "not exist or its status is NOT completed",
                    v2=f,
                )
                warnings += 1
                continue
            else:
                item = c[0]
                other_version = item.other_version.single()
                if other_version is not None:
                    skipped += 1
                    continue
                # launch here async task
                path = os.path.join(upload_dir, f)
                c.celery_app.send_task(
                    "load_v2", args=[path, item.uuid, retry], countdown=10
                )
                imported += 1

        log.info("------------------------------------")
        log.info("Total v2 content: {}", total_available)
        log.info("loading: {}", imported)
        log.info("skipped: {}", skipped)
        log.info("warning: {}", warnings)
        log.info("------------------------------------")

    def _bulk_delete(self, entity, uuids):
        deleted = 0
        if entity == "AVEntity":
            repo = CreationRepository(self.graph)
            for uuid in uuids:
                av_entity = self.graph.AVEntity.nodes.get_or_none(uuid=uuid)
                if av_entity is not None:
                    repo.delete_av_entity(av_entity)
                    deleted += 1
        elif entity == "NonAVEntity":
            repo = CreationRepository(self.graph)
            for uuid in uuids:
                non_av_entity = self.graph.NonAVEntity.nodes.get_or_none(uuid=uuid)
                if non_av_entity is not None:
                    repo.delete_non_av_entity(non_av_entity)
                    deleted += 1
        else:
            raise BadRequest(f"Entity {entity} not yet managed for deletion")
        log.debug("Deleted: {} in {}", deleted, len(uuids))
