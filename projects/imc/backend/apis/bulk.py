# -*- coding: utf-8 -*-

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

# from flask import request
# from utilities.helpers import get_api_url
# from restapi.confs import PRODUCTION
import os
import re
from shutil import copyfile
from datetime import datetime
from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from imc.tasks.services.creation_repository import CreationRepository

from imc.tasks.services.efg_xmlparser import EFG_XMLParser

from restapi.flask_ext.flask_celery import CeleryExt

logger = get_logger(__name__)


#####################################
class Bulk(GraphBaseOperations):

    allowed_actions = ('update', 'import', 'delete', 'v2')

    def check_item_type_coherence(self, resource, standard_path):
        """
        Check if the item_type of the incoming xml (standard_path)
         is the same of the existent Item in database (from resource)
        Return data:
        - if 'item_node' is None, non ha senso andare a vedere 'coherent'
        - if 'item_node' is not None, allora vado a vedere 'coherent'
        """
        logger.debug("check_item_type_coherence: resource id %s and path %s" % (
            resource.uuid, standard_path))
        coherent = False
        # check for existing item
        item_node = resource.item.single()
        if item_node is not None:
            logger.info("There is an Item associated to MetaStage %s" %
                        resource.uuid)
            # checking for item_type coherence
            existent_item_type = item_node.item_type
            if existent_item_type is None:
                logger.warning("No item_type found for item id %s" %
                               item_node.uuid)
            else:
                incoming_item_type = None
                try:
                    incoming_item_type = self.extract_item_type(standard_path)
                    if incoming_item_type is None:
                        logger.warning(
                            "No item type found for filename %s" % standard_path)
                    elif existent_item_type == incoming_item_type:
                        coherent = True
                except Exception as e:
                    logger.error("Exception %s" % e)
                    logger.error(
                        "Cannot extract item type from filename %s" % standard_path)
        return item_node, coherent

    def lookup_latest_dir(self, path):
        """
        Look for the sub-directory of path in the forms of:
        %Y-%m-%d (example 2018-04-19)
        %Y-%m-%dT%H:%M:%S.%fZ (example 2018-04-19T11:22:12.0Z)
        which name is the most recent date
        """
        logger.debug("lookup_latest_dir: input path" + path)

        POSSIBLE_FORMATS = ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S.%fZ']

        found_date = None
        found_dir = None
        dirs = [d for d in os.listdir(
            path) if os.path.isdir(os.path.join(path, d))]
        for d in dirs:
            parsed_date = None
            for format in POSSIBLE_FORMATS:
                try:
                    parsed_date = datetime.strptime(d, format)
                    break
                except Exception as e:
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
                logger.warning("cannot parse dir=" + d)
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

    @decorate.catch_error()
    @catch_graph_exceptions
    def post(self):
        logger.debug("Start bulk procedure...")

        self.graph = self.get_service_instance('neo4j')

        params = self.get_input()
        logger.debug('input: {}'.format(params))
        for allowed_action in self.__class__.allowed_actions:
            action = params.get(allowed_action)
            if action is not None:
                req_action = allowed_action
                break
        if action is None:
            raise RestApiException(
                "Bad action: expected one of %s" %
                (self.__class__.allowed_actions, ),
                status_code=hcodes.HTTP_BAD_REQUEST)

        # ##################################################################
        # Cinzia: NOV 2018: aggiungo un parametro per forzare il
        #                   reprocessing anche nel caso
        #                   che la action sia 'update'
        # ##################################################################
        if req_action == 'update':
            # check group uid
            guid = action.get('guid')
            if guid is None:
                raise RestApiException(
                    'Group id (guid) is mandatory',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            group = self.graph.Group.nodes.get_or_none(uuid=guid)
            if group is None:
                raise RestApiException(
                    'Group ID {} not found'.format(guid),
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            logger.info(
                "Update procedure for Group '{0}' ".format(group.shortname))
            # check if the parameter 'force_reprocessing' has been specified
            force_reprocessing = action.get('force_reprocessing', False)
            logger.debug('force_reprocessing: {}'.format(force_reprocessing))

            # retrieve XML files from delta upload dir
            #  (scaricato con oai-pmh solo delta rispetto all'ultimo harvest
            #    prendere dir= /uploads/<guid>/upload/<date>/ con date la data più recente)
            upload_dir = "/uploads/" + group.uuid
            # logger.debug("upload_dir %s" % upload_dir)
            upload_delta_dir = os.path.join(upload_dir, "upload")
            # logger.debug("upload_delta_dir %s" % upload_delta_dir)
            if not os.path.exists(upload_delta_dir):
                return self.force_response(
                    [], errors=["Upload dir " + upload_delta_dir + " not found"])

            # dentro la upload_delta_dir devo cercare la sotto-dir
            # che corrisponde alla data più recente
            upload_latest_dir = self.lookup_latest_dir(upload_delta_dir)

            if upload_latest_dir is None:
                logger.debug("Upload dir not found")
                return self.force_response(
                    [], errors=["Upload dir not found"])

            logger.info("Processing files from dir %s" % upload_latest_dir)

            files = [f for f in os.listdir(
                upload_latest_dir) if f.endswith('.xml')]
            total_to_be_imported = len(files)
            skipped = 0
            updated = 0
            updatedAndReprocessing = 0
            created = 0
            failed = 0
            for f in files:
                file_path = os.path.join(upload_latest_dir, f)
                filename = f
                logger.debug("Processing file %s" % filename)
                # copio il file nella directory in cui vengono uploadati il file dal Frontend
                #  come nome del file uso quello nella forma standard "<archive code>_<source id>.xml"
                #  quindi prima devo estrarre il source id dal file stesso
                logger.debug(
                    "Extracting source id from metadata file %s" % filename)
                source_id = None
                try:
                    source_id = self.extract_creation_ref(file_path)
                    if source_id is None:
                        logger.warning(
                            "No source ID found: SKIPPED filename %s" % file_path)
                        skipped += 1
                        continue
                except Exception as e:
                    logger.error("Exception %s" % e)
                    logger.error(
                        "Cannot extract source id: SKIPPED filename %s" % file_path)
                    skipped += 1
                    continue

                logger.info("Found source id %s" % source_id)

                # To use source id in the filename we must
                # replace non alpha-numeric characters with a dash
                source_id_clean = re.sub(r'[\W_]+', '-', source_id.strip())

                standard_filename = group.shortname + '_' + source_id_clean + '.xml'
                standard_path = os.path.join(upload_dir, standard_filename)
                try:
                    copyfile(file_path, standard_path)
                    logger.info("Copied file %s to file %s" %
                                (file_path, standard_path))
                except BaseException:
                    logger.warning(
                        "Cannot copy file: SKIPPED filename %s" % file_path)
                    skipped += 1
                    continue

                properties = {}
                properties['filename'] = standard_filename
                properties['path'] = standard_path

                # cerco nel database se esiste già un META_STAGE collegato a quel SOURCE_ID
                # e appartenente al gruppo
                meta_stage = None
                try:
                    query = "match (g:Group)<-[r4:IS_OWNED_BY]-(ms:MetaStage) \
                            match (ms:MetaStage)<-[r3:META_SOURCE]-(i:Item) \
                            match (i:Item)-[r2:CREATION]->(c:Creation) \
                            match (c:Creation)-[r1:RECORD_SOURCE]-> (rs:RecordSource) \
                            WHERE rs.source_id = '{source_id}' and g.uuid = '{guuid}' \
                            return ms"
                    logger.debug("Executing query: %s" % query)
                    results = self.graph.cypher(query.format(
                        source_id=source_id, guuid=group.uuid))
                    c = [self.graph.MetaStage.inflate(
                        row[0]) for row in results]
                    if len(c) > 1:
                        # TODO gestire meglio questo caso
                        # there are more than one MetaStage related to the same source id: Database incoherence!
                        logger.warning("Database incoherence: there is more than one MetaStage \
                            related to the same source id %s: SKIPPED file %s" % (source_id, standard_filename))
                        skipped += 1
                        continue

                    if len(c) == 1:
                        # Source id already exists in database
                        logger.info(
                            "MetaStage already exists in database for source id %s" % source_id)
                        meta_stage = c[0]
                        logger.debug("MetaStage=%s" % meta_stage)

                except self.graph.MetaStage.DoesNotExist:
                    logger.info(
                        "MetaStage does not exist for source id %s " % source_id)

                try:
                    # se il source_id non esiste nel database, allora possono essere due i casi:
                    #  1) e' l'import di un nuovo contenuto
                    #  2) potrebbe esistere un MetaStage associato allo stesso filename
                    #      ma senza una Creation associata perche' la volta precedente
                    #      mancava un campo mandatory e quindi l'import era fallito
                    #  Quindi prima di gestire il caso 1) devo verificare se siamo nel caso 2)
                    #  Siamo nel caso 2) se esiste MetaStage associato allo stesso filename
                    #   ma senza una Creation associata. Inoltre devo verificare che l'Item sia
                    #    del tipo del contenuto che sto caricando (immagine, video,...).
                    #  Quindi:
                    #  - se esiste MetaStage associato allo stesso filename che e' associato
                    #     a un Item di tipo diverso allora lancio eccezione e non proseguo.
                    #     (Per poter cambiare il tipo bisognerebbe aggiornare Item, Creation e
                    #     cancellare il ContentStage e ricrearlo, allora non è un aggiornamento
                    #     dei metadati, meglio cancellare tutto il pezzetto di grafo relativo e
                    #     crearne uno nuovo).
                    #  - se esiste MetaStage associato allo stesso filename che ha già una
                    #     Creation associata (e quindi avrà un source_id diverso) allora lancio
                    #     eccezione e non proseguo.
                    #
                    if meta_stage is None:

                        try:
                            resource = self.graph.MetaStage.nodes.get(
                                **properties)
                            logger.info(
                                "MetaStage already exists for %s" % standard_path)

                            # check for existing item
                            item_node, coherent = self.check_item_type_coherence(
                                resource, standard_path)
                            if item_node is not None:
                                if not coherent:
                                    logger.error(
                                        "Incoming item_type different from item_type in database for file %s" % standard_path)
                                    resource.status = 'ERROR'
                                    resource.status_message = "Incoming item_type different from item_type in database for file: " + standard_path
                                    resource.save()
                                    failed += 1
                                    continue
                                # check for existing creation
                                creation = item_node.creation.single()
                                if creation is not None:
                                    logger.error(
                                        "A creation with a different SOURCE_ID is already associated to file: %s" % standard_path)
                                    resource.status = 'ERROR'
                                    resource.status_message = "A creation with a different SOURCE_ID is already associated to file: " + standard_path
                                    resource.save()
                                    failed += 1
                                    continue

                            if force_reprocessing:
                                mode = "clean"
                                metadata_update = True
                                task = CeleryExt.import_file.apply_async(
                                    args=[standard_path, resource.uuid,
                                          mode, metadata_update],
                                    countdown=10
                                )
                                logger.debug("Task id=%s" % task.id)
                                resource.status = "UPDATING METADATA + FORCE REPROCESSING"
                                resource.task_id = task.id
                                resource.save()
                                updatedAndReprocessing += 1
                            else:
                                task = CeleryExt.update_metadata.apply_async(
                                    args=[standard_path, resource.uuid],
                                    countdown=10
                                )
                                logger.debug("Task id=%s" % task.id)
                                resource.status = "UPDATING METADATA"
                                resource.task_id = task.id
                                resource.save()
                                updated += 1

                        except self.graph.MetaStage.DoesNotExist:
                            # import di un nuovo contenuto
                            logger.debug(
                                "Creating MetaStage for file %s" % standard_path)
                            meta_stage = self.graph.MetaStage(
                                **properties).save()
                            meta_stage.ownership.connect(group)
                            logger.debug(
                                "MetaStage created for source_id %s" % source_id)
                            mode = "clean"
                            task = CeleryExt.import_file.apply_async(
                                args=[standard_path, meta_stage.uuid, mode],
                                countdown=10
                            )
                            meta_stage.status = "IMPORTING"
                            meta_stage.task_id = task.id
                            meta_stage.save()
                            created += 1

                    else:
                        # nel database esiste già un META_STAGE collegato a quel SOURCE_ID

                        #  anche qui devo fare il
                        # checking for item_type coherence
                        related_item, coherent = self.check_item_type_coherence(
                            meta_stage, standard_path)
                        if related_item is not None and not coherent:
                            logger.error(
                                "Incoming item_type different from item_type in database for file %s" % standard_path)

                            meta_stage.status = 'ERROR'
                            meta_stage.status_message = "Incoming item_type different from item_type in database for file: " + standard_path
                            meta_stage.save()
                            failed += 1
                            continue

                        # devo aggiornare nel MetaStage i campi nomefile e path con quelli che
                        #  vado a usare per l'aggiornamento dei metadati

                        # Attenzione: prima bisogna verificare che non esista già un altro metastage
                        #              che ha lo stesso standard_path che stiamo andando ad associare
                        #              al nostro meta_stage (ovviamente avranno source_id diverso)
                        #              altrimenti viene lanciata una eccezione
                        props2 = {}
                        props2['filename'] = standard_filename
                        props2['path'] = standard_path
                        try:
                            metastage_samepath = self.graph.MetaStage.nodes.get(
                                **props2)
                            logger.debug("metastage_samepath uuid: %s" %
                                         metastage_samepath.uuid)
                            logger.debug("meta_stage uuid: %s" %
                                         meta_stage.uuid)
                            # se è distinto rispetto a quello che avevo trovato per source id
                            #  allora c'è qualcosa che non va
                            if metastage_samepath.uuid != meta_stage.uuid:
                                logger.error(
                                    "Another metastage exists for file %s" % standard_path)
                                meta_stage.status = 'ERROR'
                                meta_stage.status_message = "Another metastage exists for file " + standard_path
                                meta_stage.save()
                                failed += 1
                                continue

                        except self.graph.MetaStage.DoesNotExist:
                            logger.info(
                                "MetaStage does not exist for %s" % standard_path)
                            # aggiorno nel MetaStage i campi nomefile e path
                            meta_stage.filename = standard_filename
                            meta_stage.path = standard_path
                            meta_stage.save()

                        if force_reprocessing:
                            # update dei metadati e reprocessing
                            logger.info(
                                "Starting task import_file for meta_stage.uuid %s" % meta_stage.uuid)
                            mode = "clean"
                            metadata_update = True
                            task = CeleryExt.import_file.apply_async(
                                args=[standard_path, meta_stage.uuid,
                                      mode, metadata_update],
                                ountdown=10
                            )
                            logger.debug("Task id=%s" % task.id)
                            meta_stage.status = "UPDATING METADATA + FORCE REPROCESSING"
                            meta_stage.task_id = task.id
                            meta_stage.save()
                            updatedAndReprocessing += 1
                        else:
                            # update dei soli metadati
                            logger.info(
                                "Starting task update_metadata for meta_stage.uuid %s" % meta_stage.uuid)
                            task = CeleryExt.update_metadata.apply_async(
                                args=[standard_path, meta_stage.uuid],
                                countdown=10
                            )
                            logger.info("Task id=%s" % task.id)
                            meta_stage.status = "UPDATING METADATA"
                            meta_stage.task_id = task.id
                            meta_stage.save()
                            updated += 1

                except Exception as e:
                    logger.error(
                        "Update operation failed for filename %s, error message=%s" % (file_path, e))
                    failed += 1
                    continue

            logger.info("------------------------------------")
            logger.info("Total record: {}".format(total_to_be_imported))
            logger.info("updating: {}".format(updated))
            logger.info("updating and reprocessing: {}".format(
                updatedAndReprocessing))
            logger.info("creating: {}".format(created))
            logger.info("skipped {}".format(skipped))
            logger.info("failed {}".format(failed))
            logger.info("------------------------------------")

            return self.force_response(
                "Bulk request accepted", code=hcodes.HTTP_OK_ACCEPTED)

        # ##################################################################
        elif req_action == 'import':
            # check group uid
            guid = action.get('guid')
            if guid is None:
                raise RestApiException(
                    'Group id (guid) is mandatory',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            group = self.graph.Group.nodes.get_or_none(uuid=guid)
            if group is None:
                raise RestApiException(
                    'Group ID {} not found'.format(guid),
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            update = bool(action.get('update'))
            mode = action.get('mode') or 'skip'
            retry = bool(action.get('retry'))
            logger.info(
                "Import procedure for Group '{0}' (mode: {1}; update {2}; retry {3})".format(
                    group.shortname, mode, update, retry))

            # retrieve XML files from upload dir
            upload_dir = os.path.join("/uploads", group.uuid)
            if not os.path.exists(upload_dir):
                return self.force_response(
                    [], errors=["Upload dir not found"])

            files = [f for f in os.listdir(upload_dir) if f.endswith('.xml')]
            total_to_be_imported = len(files)
            skipped = 0
            imported = 0
            for f in files:
                path = os.path.join(upload_dir, f)
                filename = f
                properties = {}
                properties['filename'] = filename
                properties['path'] = path

                # ignore previous failures
                if not retry:
                    try:
                        # props = {'status': 'ERROR', 'filename': f} #OLD
                        props = {'status': 'ERROR', 'path': path}
                        self.graph.MetaStage.nodes.get(**props)
                        skipped += 1
                        logger.debug(
                            "SKIPPED already imported with ERROR. Filename {}".format(path))
                        continue
                    except self.graph.MetaStage.DoesNotExist:
                        pass

                if not update:
                    query = "match (n:MetaStage) WHERE n.path = '{path}' \
                              match (n)-[r1:META_SOURCE]-(i:Item) \
                              match (i)-[r2:CREATION]->(c:Creation) \
                              return c"
                    results = self.graph.cypher(query.format(path=path))
                    c = [self.graph.Creation.inflate(
                        row[0]) for row in results]
                    if len(c) == 1:
                        skipped += 1
                        logger.debug(
                            "SKIPPED filename: {0}. Creation uuid: {1}".format(
                                path, c[0].uuid))
                        continue
                logger.info("Importing metadata file: {}".format(path))
                try:
                    resource = self.graph.MetaStage.nodes.get(**properties)
                    logger.debug("Resource already exist for %s" % path)
                except self.graph.MetaStage.DoesNotExist:
                    resource = self.graph.MetaStage(**properties).save()
                    resource.ownership.connect(group)
                    logger.debug("Metadata Resource created for %s" % path)

                task = CeleryExt.import_file.apply_async(
                    args=[path, resource.uuid, mode],
                    countdown=10
                )

                resource.status = "IMPORTING"
                resource.task_id = task.id
                resource.save()
                imported += 1

            logger.info("------------------------------------")
            logger.info("Total record: {}".format(total_to_be_imported))
            logger.info("importing: {}".format(imported))
            logger.info("skipped {}".format(skipped))
            logger.info("------------------------------------")

            return self.force_response(
                "Bulk request accepted", code=hcodes.HTTP_OK_ACCEPTED)

        # ##################################################################
        elif req_action == 'v2':
            # check group uid
            guid = action.get('guid')
            if guid is None:
                raise RestApiException(
                    'Group id (guid) is mandatory',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            group = self.graph.Group.nodes.get_or_none(uuid=guid)
            if group is None:
                raise RestApiException(
                    'Group ID {} not found'.format(guid),
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            retry = bool(action.get('retry'))
            logger.info(
                "V2 procedure for Group '{}'".format(group.shortname))

            # retrieve v2_ XML files from upload dir
            upload_dir = os.path.join("/uploads", group.uuid)
            if not os.path.exists(upload_dir):
                return self.force_response(
                    [], errors=["Upload dir not found"])

            # v2_ is used for the 'other version' (exclude .xml)
            files = [f for f in os.listdir(upload_dir) if not f.endswith(
                '.xml') and re.match(r'^v2_.*', f, re.I)]
            total_available = len(files)
            if total_available == 0:
                raise RestApiException(
                    'No v2 content for group {}'.format(group.shortname),
                    status_code=hcodes.HTTP_OK_NORESPONSE)
            logger.info(
                "Total v2 files currently available: {}".format(total_available))
            skipped = 0
            imported = 0
            for f in files:
                # cut away prefix and look for the related content
                origin = f.split("_", 1)[1]
                source_path = os.path.join(upload_dir, origin)
                query = "MATCH (n:ContentStage {{path:'{path}', status:'COMPLETED'}})" \
                        "<-[:CONTENT_SOURCE]-(i:Item) RETURN i".format(
                            path=source_path)
                results = self.graph.cypher(query)
                c = [self.graph.Item.inflate(row[0]) for row in results]
                if len(c) == 0:
                    logger.warn('Cannot load {v2} because origin content does '
                                'not exist or its status is NOT completed')
                    skipped += 1
                    continue
                else:
                    item = c[0]
                    other_version = item.other_version.single()
                    if other_version is not None:
                        skipped += 1
                        continue
                    # launch here async task
                    path = os.path.join(upload_dir, f)
                    task = CeleryExt.load_v2.apply_async(
                        args=[path, item.uuid],
                        countdown=10
                    )
                    imported += 1

            logger.info("------------------------------------")
            logger.info("Total v2 content: {}".format(total_available))
            logger.info("loading: {}".format(imported))
            logger.info("skipped {}".format(skipped))
            logger.info("------------------------------------")

        # ##################################################################
        elif req_action == 'delete':
            entity = action.get('entity')
            if entity is None:
                raise RestApiException(
                    'Entity is mandatory',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            labels_query = "MATCH (n) \
                            WITH DISTINCT labels(n) AS labels \
                            UNWIND labels AS label \
                            RETURN DISTINCT label"
            labels = [row[0] for row in self.graph.cypher(labels_query)]
            if entity not in labels:
                raise RestApiException(
                    'Invalid or missing entity label for {}'.format(entity),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            uuids = action.get('uuids')
            if uuids is None:
                raise RestApiException(
                    'Expected list of uuid',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            if isinstance(uuids, str):
                if uuids != 'all':
                    raise RestApiException(
                        'Expected list of uuid',
                        status_code=hcodes.HTTP_BAD_REQUEST)
                all_query = "match (n:{}) return n.uuid".format(entity)
                uuids = [row[0] for row in self.graph.cypher(all_query)]
            deleted = 0
            if entity == 'AVEntity':
                repo = CreationRepository(self.graph)
                for uuid in uuids:
                    av_entity = self.graph.AVEntity.nodes.get_or_none(
                        uuid=uuid)
                    if av_entity is not None:
                        repo.delete_av_entity(av_entity)
                        deleted += 1
            elif entity == 'NonAVEntity':
                repo = CreationRepository(self.graph)
                for uuid in uuids:
                    non_av_entity = self.graph.NonAVEntity.nodes.get_or_none(
                        uuid=uuid)
                    if non_av_entity is not None:
                        repo.delete_non_av_entity(non_av_entity)
                        deleted += 1
            else:
                raise RestApiException(
                    'Entity {} not yet managed for deletion'.format(entity),
                    status_code=hcodes.HTTP_BAD_REQUEST)
            logger.debug("Deleted: {} in {}".format(deleted, len(uuids)))
            return self.empty_response()

        # ##################################################################
        # add here any other bulk request

        return self.force_response(
            "Bulk request accepted", code=hcodes.HTTP_OK_ACCEPTED)
