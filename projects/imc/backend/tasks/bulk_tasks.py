import os
import re
from shutil import copyfile

from imc.tasks.services.efg_xmlparser import EFG_XMLParser
from restapi.connectors import neo4j
from restapi.connectors.celery import CeleryExt
from restapi.utilities.logs import log


def extract_item_type(path):
    """Extract the creation type from the incoming XML file."""
    parser = EFG_XMLParser()
    return parser.get_creation_type(path)


def check_item_type_coherence(resource, standard_path):
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
                incoming_item_type = extract_item_type(standard_path)
                if incoming_item_type is None:
                    log.warning("No item type found for filename {}", standard_path)
                elif existent_item_type == incoming_item_type:
                    coherent = True
            except Exception as e:
                log.error("Exception {}", e)
                log.error("Cannot extract item type from filename {}", standard_path)
    return item_node, coherent


@CeleryExt.task()
def bulk_update(self, guid, upload_dir, target_dir, force_reprocessing=False):
    log.info(f"Bulk update: processing files from dir {upload_dir}")

    graph = neo4j.get_instance()

    group = graph.Group.nodes.get_or_none(uuid=guid)
    if group is None:
        raise LookupError(f"Group ID {guid} not found")

    xml_parser = EFG_XMLParser()
    files = [f for f in os.listdir(upload_dir) if f.endswith(".xml")]
    total_to_be_imported = len(files)
    skipped = 0
    updated = 0
    updated_and_reprocessing = 0
    created = 0
    failed = 0
    for f in files:
        file_path = os.path.join(upload_dir, f)
        filename = f
        log.debug("Processing file {}", filename)
        # copy the file in the directory where the file is uploaded from the Frontend.
        # As filename I use the one in the standard form "<archive code>_<source id>.xml"
        # so first I have to extract the source id from the file itself
        log.debug("Extracting source id from metadata file {}", filename)
        source_id = None
        try:
            source_id = xml_parser.get_creation_ref(file_path)
            if source_id is None:
                log.warning(f"No source ID found: SKIPPED filename {file_path}")
                skipped += 1
                continue
        except Exception as e:
            log.error("Exception {}", e)
            log.error(f"Cannot extract source id: SKIPPED filename {file_path}")
            skipped += 1
            continue

        log.info(f"Found source id {source_id}")

        # To use source id in the filename we must
        # replace non alpha-numeric characters with a dash
        source_id_clean = re.sub(r"[\W_]+", "-", source_id.strip())

        standard_filename = group.shortname + "_" + source_id_clean + ".xml"
        standard_path = os.path.join(target_dir, standard_filename)
        try:
            copyfile(file_path, standard_path)
            log.info(f"Copied file {file_path} to file {standard_path}")
        except BaseException as e:
            log.warning(f"SKIPPED - Cannot copy file '{file_path}': {e}")
            skipped += 1
            continue

        properties = {"filename": standard_filename, "path": standard_path}

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
            # log.debug("Executing query: \n{}", query)
            results = graph.cypher(query.format(source_id=source_id, guuid=group.uuid))
            c = [graph.MetaStage.inflate(row[0]) for row in results]
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

        except graph.MetaStage.DoesNotExist:
            log.info(f"MetaStage does not exist for source id {source_id}")

        try:
            """
            if the source_id doesn't exist in the database,
            then there may be two cases:
             1) import of a new content
             2) there may be a MetaStage associated with the same filename but without
                an associated Creation because the previous time a mandatory field was
                missing and therefore the import had failed
             So before handling case 1) I have to check if we are in case 2)
             We are in case 2) if MetaStage exists associated with the same filename but
             without an associated Creation. Also I have to verify that the Item is of the
             type of the content I am uploading (image, video, ...).
             Then:
             - if MetaStage exists associated with the same filename which is associated
               with a different Item then I throw exception and do not continue.
               (In order to change the type, it would be necessary to update Item,
               Creation and delete the ContentStage and recreate it,
               then it is not an update of the metadata, better to delete the whole piece
               of relative graph and create a new one).
             - if MetaStage exists associated with the same filename which already has an
               associated Creation (and therefore will have a different source_id)
               then I throw an exception and do not continue.
            """
            if meta_stage is None:

                try:
                    resource = graph.MetaStage.nodes.get(**properties)
                    log.info(f"MetaStage already exists for {standard_path}")

                    # check for existing item
                    item_node, coherent = check_item_type_coherence(
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
                        task = CeleryExt.celery_app.send_task(
                            "import_file",
                            args=(
                                standard_path,
                                resource.uuid,
                                mode,
                                metadata_update,
                            ),
                            countdown=10,
                        )
                        log.debug("Task id={}", task.id)
                        resource.status = "UPDATING METADATA + FORCE REPROCESSING"
                        resource.task_id = task.id
                        resource.save()
                        updated_and_reprocessing += 1
                    else:
                        task = CeleryExt.celery_app.send_task(
                            "update_metadata",
                            args=(
                                standard_path,
                                resource.uuid,
                            ),
                            countdown=10,
                        )
                        log.debug("Task id={}", task.id)
                        resource.status = "UPDATING METADATA"
                        resource.task_id = task.id
                        resource.save()
                        updated += 1

                except graph.MetaStage.DoesNotExist:
                    # import of a new content
                    log.debug("Creating MetaStage for file {}", standard_path)
                    meta_stage = graph.MetaStage(**properties).save()
                    meta_stage.ownership.connect(group)
                    log.debug("MetaStage created for source_id {}", source_id)
                    mode = "clean"
                    task = CeleryExt.celery_app.send_task(
                        "import_file",
                        args=(
                            standard_path,
                            meta_stage.uuid,
                            mode,
                        ),
                        countdown=10,
                    )
                    meta_stage.status = "IMPORTING"
                    meta_stage.task_id = task.id
                    meta_stage.save()
                    created += 1

            else:
                # a META_STAGE linked to that SOURCE_ID already exists in the db
                # here too I have to check for item_type coherence
                related_item, coherent = check_item_type_coherence(
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
                """
                I have to update in the MetaStage the filename and path fields with the ones I am going to use
                for updating the metadata

                Caution:
                first you need to verify that there is not already another MetaStage that has the same
                standard_path that we are going to associate with our meta_stage
                (obviously they will have a different source_id) otherwise an exception is thrown.
                """
                props2 = {}
                props2["filename"] = standard_filename
                props2["path"] = standard_path
                try:
                    metastage_samepath = graph.MetaStage.nodes.get(**props2)
                    log.debug("metastage_samepath uuid: {}", metastage_samepath.uuid)
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

                except graph.MetaStage.DoesNotExist:
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
                    task = CeleryExt.celery_app.send_task(
                        "import_file",
                        args=(
                            standard_path,
                            meta_stage.uuid,
                            mode,
                            metadata_update,
                        ),
                        countdown=10,
                    )
                    log.debug("Task id={}", task.id)
                    meta_stage.status = "UPDATING METADATA + FORCE REPROCESSING"
                    meta_stage.task_id = task.id
                    meta_stage.save()
                    updated_and_reprocessing += 1
                else:
                    # metadata update ONLY
                    log.info(
                        "Starting task update_metadata for meta_stage.uuid {}",
                        meta_stage.uuid,
                    )
                    task = CeleryExt.celery_app.send_task(
                        "update_metadata",
                        args=(
                            standard_path,
                            meta_stage.uuid,
                        ),
                        countdown=10,
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
    log.info(f"total records: {total_to_be_imported}")
    log.info(f"updating: {updated}")
    log.info(f"updating and reprocessing: {updated_and_reprocessing}")
    log.info(f"creating: {created}")
    log.info(f"skipped: {skipped}")
    log.info(f"failed: {failed}")
    log.info("------------------------------------")
