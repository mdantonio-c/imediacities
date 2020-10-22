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
from shutil import copyfile

from imc.endpoints import IMCEndpoint
from imc.models import BulkSchema
from imc.tasks.services.creation_repository import CreationRepository
from imc.tasks.services.efg_xmlparser import EFG_XMLParser
from restapi import decorators
from restapi.exceptions import BadRequest, NotFound
from restapi.services.authentication import Role
from restapi.utilities.htmlcodes import hcodes
from restapi.utilities.logs import log


#####################################
class Bulk(IMCEndpoint):

    labels = ["bulk"]

    def check_item_type_coherence(self, resource, standard_path):
        """
        Check if the item_type of the incoming xml (standard_path) is the same of the existent Item in the database
        (from resource).
        :param resource:
        :param standard_path:
        :return: item node and coherent boolean
        """
        log.debug(
            "check_item_type_coherence: resource id {} and path {}",
            resource.uuid,
            standard_path,
        )
        coherent = False
        # check for existing item
        item_node = resource.item.single()
        if item_node is not None:
            log.info("There is an Item associated to MetaStage {}", resource.uuid)
            # checking for item_type coherence
            existent_item_type = item_node.item_type
            if existent_item_type is None:
                log.warning("No item_type found for item id {}", item_node.uuid)
            else:
                incoming_item_type = None
                try:
                    incoming_item_type = self.extract_item_type(standard_path)
                    if incoming_item_type is None:
                        log.warning("No item type found for filename {}", standard_path)
                    elif existent_item_type == incoming_item_type:
                        coherent = True
                except Exception as e:
                    log.error("Exception {}", e)
                    log.error(
                        "Cannot extract item type from filename {}", standard_path
                    )
        return item_node, coherent

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

    def extract_creation_ref(self, path):
        """
        Extract the source id reference from the XML file
        """
        parser = EFG_XMLParser()
        return parser.get_creation_ref(path)

    def extract_item_type(self, path):
        """
        Extract the creation type from the incoming XML file.
        """
        parser = EFG_XMLParser()
        return parser.get_creation_type(path)

    @decorators.auth.require_all(Role.ADMIN)
    @decorators.catch_graph_exceptions
    @decorators.use_kwargs(BulkSchema)
    @decorators.endpoint(
        path="/bulk",
        summary="Perform many operations such as import, update, delete etc.",
        description="The bulk api makes it possible to perform many operations in a single api call",
        responses={202: "Bulk action successfully accepted", 400: "Bad request."},
    )
    def post(self, **req_action):
        log.debug("Start bulk procedure...")

        self.graph = self.get_service_instance("neo4j")
        self.celery = self.get_service_instance("celery")

        if action := req_action.get("update"):
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

            # inside the upload_delta_dir I have to look for the sub-dir that corresponds to the most recent date
            upload_latest_dir = self.lookup_latest_dir(upload_delta_dir)

            if upload_latest_dir is None:
                log.debug("Upload dir not found")
                raise NotFound("Upload dir not found")

            log.info("Processing files from dir {}", upload_latest_dir)

            files = [f for f in os.listdir(upload_latest_dir) if f.endswith(".xml")]
            total_to_be_imported = len(files)
            skipped = 0
            updated = 0
            updatedAndReprocessing = 0
            created = 0
            failed = 0
            for f in files:
                file_path = os.path.join(upload_latest_dir, f)
                filename = f
                log.debug("Processing file {}", filename)
                # copy the file in the directory where the file is uploaded from the Frontend.
                # As filename I use the one in the standard form "<archive code>_<source id>.xml"
                # so first I have to extract the source id from the file itself
                log.debug("Extracting source id from metadata file {}", filename)
                source_id = None
                try:
                    source_id = self.extract_creation_ref(file_path)
                    if source_id is None:
                        log.warning(
                            "No source ID found: SKIPPED filename {}", file_path
                        )
                        skipped += 1
                        continue
                except Exception as e:
                    log.error("Exception {}", e)
                    log.error(
                        "Cannot extract source id: SKIPPED filename {}", file_path
                    )
                    skipped += 1
                    continue

                log.info("Found source id {}", source_id)

                # To use source id in the filename we must
                # replace non alpha-numeric characters with a dash
                source_id_clean = re.sub(r"[\W_]+", "-", source_id.strip())

                standard_filename = group.shortname + "_" + source_id_clean + ".xml"
                standard_path = os.path.join(upload_dir, standard_filename)
                try:
                    copyfile(file_path, standard_path)
                    log.info("Copied file {} to file {}", file_path, standard_path)
                except BaseException:
                    log.warning("Cannot copy file: SKIPPED filename {}", file_path)
                    skipped += 1
                    continue

                properties = {}
                properties["filename"] = standard_filename
                properties["path"] = standard_path

                # I look in the db if there is already a META_STAGE connected to that SOURCE_ID
                # and belonging to the group
                meta_stage = None
                try:
                    query = "match (g:Group)<-[r4:IS_OWNED_BY]-(ms:MetaStage) \
                            match (ms:MetaStage)<-[r3:META_SOURCE]-(i:Item) \
                            match (i:Item)-[r2:CREATION]->(c:Creation) \
                            match (c:Creation)-[r1:RECORD_SOURCE]-> (rs:RecordSource) \
                            WHERE rs.source_id = '{source_id}' and g.uuid = '{guuid}' \
                            return ms"
                    log.debug("Executing query: {}", query)
                    results = self.graph.cypher(
                        query.format(source_id=source_id, guuid=group.uuid)
                    )
                    c = [self.graph.MetaStage.inflate(row[0]) for row in results]
                    if len(c) > 1:
                        # TODO better manage this case
                        # there are more than one MetaStage related to
                        # the same source id: Database incoherence!
                        log.warning(
                            "Database incoherence: there is more than one MetaStage \
                            related to the same source id {}: SKIPPED file {}",
                            source_id,
                            standard_filename,
                        )
                        skipped += 1
                        continue

                    if len(c) == 1:
                        # Source id already exists in database
                        log.info(
                            "MetaStage already exists in database for source id {}",
                            source_id,
                        )
                        meta_stage = c[0]
                        log.debug("MetaStage={}", meta_stage)

                except self.graph.MetaStage.DoesNotExist:
                    log.info("MetaStage does not exist for source id {}", source_id)

                try:
                    # if the source_id doesn't exist in the database,
                    # then there may be two cases:
                    #  1) import of a new content
                    #  2) there may be a MetaStage associated with the same filename but without
                    #     an associated Creation because the previous time a mandatory field was
                    #     missing and therefore the import had failed
                    #  So before handling case 1) I have to check if we are in case 2)
                    #  We are in case 2) if MetaStage exists associated with the same filename but
                    #  without an associated Creation. Also I have to verify that the Item is of the
                    #  type of the content I am uploading (image, video, ...).
                    #  Then:
                    #  - if MetaStage exists associated with the same filename which is associated
                    #    with a different Item then I throw exception and do not continue.
                    #    (In order to change the type, it would be necessary to update Item,
                    #    Creation and delete the ContentStage and recreate it,
                    #    then it is not an update of the metadata, better to delete the whole piece
                    #    of relative graph and create a new one).
                    #  - if MetaStage exists associated with the same filename which already has an
                    #    associated Creation (and therefore will have a different source_id)
                    #    then I throw an exception and do not continue.
                    if meta_stage is None:

                        try:
                            resource = self.graph.MetaStage.nodes.get(**properties)
                            log.info("MetaStage already exists for {}", standard_path)

                            # check for existing item
                            item_node, coherent = self.check_item_type_coherence(
                                resource, standard_path
                            )
                            if item_node is not None:
                                if not coherent:
                                    resource.status = "ERROR"
                                    resource.status_message = "Incoming item_type different from item_type in database for file: {}".format(
                                        standard_path
                                    )
                                    resource.save()
                                    log.error(resource.status_message)
                                    failed += 1
                                    continue
                                # check for existing creation
                                creation = item_node.creation.single()
                                if creation is not None:
                                    resource.status = "ERROR"
                                    resource.status_message = "A creation with a different SOURCE_ID is already associated to file: {}".format(
                                        standard_path
                                    )
                                    resource.save()
                                    log.error(resource.status_message)
                                    failed += 1
                                    continue

                            if force_reprocessing:
                                mode = "clean"
                                metadata_update = True
                                task = self.celery.import_file.apply_async(
                                    args=[
                                        standard_path,
                                        resource.uuid,
                                        mode,
                                        metadata_update,
                                    ],
                                    countdown=10,
                                )
                                log.debug("Task id={}", task.id)
                                resource.status = (
                                    "UPDATING METADATA + FORCE REPROCESSING"
                                )
                                resource.task_id = task.id
                                resource.save()
                                updatedAndReprocessing += 1
                            else:
                                task = self.celery.update_metadata.apply_async(
                                    args=[standard_path, resource.uuid], countdown=10
                                )
                                log.debug("Task id={}", task.id)
                                resource.status = "UPDATING METADATA"
                                resource.task_id = task.id
                                resource.save()
                                updated += 1

                        except self.graph.MetaStage.DoesNotExist:
                            # import of a new content
                            log.debug("Creating MetaStage for file {}", standard_path)
                            meta_stage = self.graph.MetaStage(**properties).save()
                            meta_stage.ownership.connect(group)
                            log.debug("MetaStage created for source_id {}", source_id)
                            mode = "clean"
                            task = self.celery.import_file.apply_async(
                                args=[standard_path, meta_stage.uuid, mode],
                                countdown=10,
                            )
                            meta_stage.status = "IMPORTING"
                            meta_stage.task_id = task.id
                            meta_stage.save()
                            created += 1

                    else:
                        # a META_STAGE linked to that SOURCE_ID already exists in the db
                        # here too I have to check for item_type coherence
                        related_item, coherent = self.check_item_type_coherence(
                            meta_stage, standard_path
                        )
                        if related_item is not None and not coherent:
                            meta_stage.status = "ERROR"
                            meta_stage.status_message = (
                                "Incoming item_type different from item_type in database for "
                                "file: {}".format(standard_path)
                            )
                            meta_stage.save()
                            log.error(meta_stage.status_message)
                            failed += 1
                            continue

                        # I have to update in the MetaStage the filename and path fields with the ones I am going to use
                        # for updating the metadata

                        # Caution:
                        # first you need to verify that there is not already another MetaStage that has the same
                        # standard_path that we are going to associate with our meta_stage
                        # (obviously they will have a different source_id) otherwise an exception is thrown.
                        props2 = {}
                        props2["filename"] = standard_filename
                        props2["path"] = standard_path
                        try:
                            metastage_samepath = self.graph.MetaStage.nodes.get(
                                **props2
                            )
                            log.debug(
                                "metastage_samepath uuid: {}", metastage_samepath.uuid
                            )
                            log.debug("meta_stage uuid: {}", meta_stage.uuid)
                            # if it is distinct from what i had found by source id then there is something wrong
                            if metastage_samepath.uuid != meta_stage.uuid:
                                log.error(
                                    "Another metastage exists for file {}",
                                    standard_path,
                                )
                                meta_stage.status = "ERROR"
                                meta_stage.status_message = (
                                    "Another metastage exists for file " + standard_path
                                )
                                meta_stage.save()
                                failed += 1
                                continue

                        except self.graph.MetaStage.DoesNotExist:
                            log.info("MetaStage does not exist for {}", standard_path)
                            # update the filename and path fields in the MetaStage
                            meta_stage.filename = standard_filename
                            meta_stage.path = standard_path
                            meta_stage.save()

                        if force_reprocessing:
                            # metadata update and reprocessing
                            log.info(
                                "Starting task import_file for meta_stage.uuid {}",
                                meta_stage.uuid,
                            )
                            mode = "clean"
                            metadata_update = True
                            task = self.celery.import_file.apply_async(
                                args=[
                                    standard_path,
                                    meta_stage.uuid,
                                    mode,
                                    metadata_update,
                                ],
                                ountdown=10,
                            )
                            log.debug("Task id={}", task.id)
                            meta_stage.status = "UPDATING METADATA + FORCE REPROCESSING"
                            meta_stage.task_id = task.id
                            meta_stage.save()
                            updatedAndReprocessing += 1
                        else:
                            # metadata update ONLY
                            log.info(
                                "Starting task update_metadata for meta_stage.uuid {}",
                                meta_stage.uuid,
                            )
                            task = self.celery.update_metadata.apply_async(
                                args=[standard_path, meta_stage.uuid], countdown=10
                            )
                            log.info("Task id={}", task.id)
                            meta_stage.status = "UPDATING METADATA"
                            meta_stage.task_id = task.id
                            meta_stage.save()
                            updated += 1

                except Exception as e:
                    log.error(
                        "Update operation failed for filename {}, error message={}",
                        file_path,
                        e,
                    )
                    failed += 1
                    continue

            log.info("------------------------------------")
            log.info("Total record: {}", total_to_be_imported)
            log.info("updating: {}", updated)
            log.info("updating and reprocessing: {}", updatedAndReprocessing)
            log.info("creating: {}", created)
            log.info("skipped {}", skipped)
            log.info("failed {}", failed)
            log.info("------------------------------------")

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
            "Import procedure for Group '{0}' (mode: {1}; update {2}; retry {3})",
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

            task = self.celery.import_file.apply_async(
                args=[path, resource.uuid, mode], countdown=10
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
                self.celery.load_v2.apply_async(
                    args=[path, item.uuid, retry], countdown=10
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
