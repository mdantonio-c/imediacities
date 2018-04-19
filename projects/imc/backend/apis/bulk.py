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

    allowed_actions = ('update', 'import', 'delete')

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
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) ]
        for d in dirs:
            parsed_date = None
            for format in POSSIBLE_FORMATS :
                try:
                    parsed_date = datetime.strptime(d, format)
                    break;
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
        if req_action == 'update':
            # check group uid
            guid = action.get('guid')
            if guid is None:
                raise RestApiException(
                    'Group id (guid) is mandatory',
                    status_code=hcodes.HTTP_BAD_REQUEST)
            group = self.graph.Group.nodes.get(uuid=guid)
            if group is None:
                raise RestApiException(
                    'Group ID {} not found'.format(guid),
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            logger.info(
                "Update procedure for Group '{0}' ".format(group.shortname))

            # retrieve XML files from delta upload dir
            #  (scaricato con oai-pmh solo delta rispetto all'ultimo harvest
            #    prendere dir= guid/upload/date con date la data più recente)
            upload_dir = "/uploads/" + group.uuid
            #logger.debug("upload_dir %s" % upload_dir)
            upload_delta_dir = os.path.join(upload_dir, "upload")
            #logger.debug("upload_delta_dir %s" % upload_delta_dir)
            if not os.path.exists(upload_delta_dir):
                return self.force_response(
                    [], errors=["Upload dir " + upload_delta_dir + " not found"])

            # dentro la upload_delta_dir devo cercare la sotto-dir 
            #  che corrisponde alla data più recente
            upload_latest_dir = self.lookup_latest_dir(upload_delta_dir)
            
            if upload_latest_dir is None:
                logger.debug("Upload dir not found")
                return self.force_response(
                    [], errors=["Upload dir not found"])

            logger.debug("Processing file from dir %s" % upload_latest_dir)

            files = [f for f in os.listdir(upload_latest_dir) if f.endswith('.xml')]
            total_to_be_imported = len(files)
            skipped = 0
            updated = 0
            created = 0
            failed = 0
            for f in files:
                file_path = os.path.join(upload_latest_dir, f)
                filename = f
                logger.debug("Processing file %s" % filename)
                # copio il file nella directory in cui vengono uploadati il file dal Frontend
                #  come nome del file uso quello nella forma standard "<archive code>_<source id>.xml"
                #  quindi prima devo estrarre il source id dal file stesso
                logger.debug("Extracting source id from metadata file %s" % filename)
                source_id = self.extract_creation_ref(file_path)
                if source_id is None:
                    logger.debug("No source ID found: SKIPPED filename %s" % file_path)
                    skipped += 1
                    continue

                logger.debug("Found source id %s" % source_id)
                standard_filename = group.shortname + '_' + source_id + '.xml'
                standard_path = os.path.join(upload_dir, standard_filename)
                try:
                    copyfile(file_path, standard_path)
                    logger.debug("Copied file %s to file %s" % (file_path, standard_path))
                except BaseException:
                    logger.debug("Cannot copy file: SKIPPED filename %s" % file_path)
                    skipped += 1
                    continue

                properties = {}
                properties['filename'] = standard_filename
                properties['path'] = standard_path

                #cerco nel database se esiste già un META_STAGE collegato a quel SOURCE_ID
                meta_stage = None
                try:
                    query = "match (ms:MetaStage)<-[r3:META_SOURCE]-(i:Item) \
                            match (i:Item)-[r2:CREATION]->(c:Creation) \
                            match (c:Creation)-[r1:RECORD_SOURCE]-> (rs:RecordSource) \
                            WHERE rs.source_id = '{source_id}' \
                            return ms"
                    logger.debug("Executing query: %s" % query)
                    results = self.graph.cypher(query.format(source_id=source_id))
                    c = [self.graph.MetaStage.inflate(row[0]) for row in results]
                    if len(c) > 1:
                        # there are more than one MetaStage related to the same source id: Database incoherence!
                        logger.info("Database incoherence: there are more than one MetaStage \
                            related to the same source id %s: SKIPPED filename %s" % (source_id,standard_filename))
                        skipped += 1
                        continue

                    if len(c) == 1:
                        # Source id already exists in database
                        logger.debug("MetaStage already exists in database for source id %s" % source_id)
                        meta_stage = c[0]
                        logger.debug("MetaStage=%s" % meta_stage)

                except self.graph.MetaStage.DoesNotExist:
                    logger.debug("MetaStage not exist for source id %s " % source_id)

                try:
                    if meta_stage is None:
                        # import di un nuovo contenuto
                        logger.debug("Creating MetaStage for file %s" % standard_path)
                        meta_stage = self.graph.MetaStage(**properties).save()
                        meta_stage.ownership.connect(group)
                        logger.debug("MetaStage created for source_id %s" % source_id)
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
                        #update dei soli metadati
                        logger.debug("Starting task update_metadata for meta_stage.uuid %s" % meta_stage.uuid)

                        # devo aggiornare nel MetaStage i campi nomefile e path con quelli che
                        #  vado a usare per l'aggiornamento dei metadati
                        meta_stage.filename = standard_filename
                        meta_stage.path = standard_path
                        meta_stage.save()

                        task = CeleryExt.update_metadata.apply_async(
                            args=[standard_path, meta_stage.uuid],
                            countdown=10
                        )
                        logger.debug("Task id=%s" % task.id)
                        meta_stage.status = "UPDATING METADATA"
                        meta_stage.task_id = task.id
                        meta_stage.save()
                        updated += 1
                except Exception as e:
                    logger.debug("Update operation failed for filename %s, error message=%s" % (file_path,e))
                    failed += 1
                    continue

            logger.info("------------------------------------")
            logger.info("Total record: {}".format(total_to_be_imported))
            logger.info("updating: {}".format(updated))
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
            group = self.graph.Group.nodes.get(uuid=guid)
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
                        props = {'status': 'ERROR', 'filename': f}
                        self.graph.MetaStage.nodes.get(**props)
                        skipped += 1
                        logger.debug(
                            "SKIPPED already imported with ERROR. Filename {}".format(filename))
                        continue
                    except self.graph.MetaStage.DoesNotExist:
                        pass

                if not update:
                    query = "match (n:MetaStage) WHERE n.filename = '{filename}' \
                              match (n)-[r1:META_SOURCE]-(i:Item) \
                              match (i)-[r2:CREATION]->(c:Creation) \
                              return c"
                    results = self.graph.cypher(query.format(filename=f))
                    c = [self.graph.Creation.inflate(row[0]) for row in results]
                    if len(c) == 1:
                        skipped += 1
                        logger.debug(
                            "SKIPPED filename: {0}. Creation uuid: {1}".format(
                                filename, c[0].uuid))
                        continue
                logger.info("Importing metadata file: {}".format(filename))
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
                    av_entity = self.graph.AVEntity.nodes.get_or_none(uuid=uuid)
                    if av_entity is not None:
                        repo.delete_av_entity(av_entity)
                        deleted += 1
            elif entity == 'NonAVEntity':
                repo = CreationRepository(self.graph)
                for uuid in uuids:
                    non_av_entity = self.graph.NonAVEntity.nodes.get_or_none(uuid=uuid)
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
