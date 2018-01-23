# -*- coding: utf-8 -*-

"""
Bulk endpoint.

The bulk API makes it possible to perform many operations in a single API call.
e.g.
POST api/bulk
{"import": {"guid":"9fea0424-1280-4bba-9be9-d6071ad32354", "mode": "skip", "update":true}}
{"delete": {"entity":"AVEntity", "uuids": ["10fe3277-2d25-4de0-8e1d-bdd2a5dd6895", etc.]}}

@author: Giuseppe Trotta <g.trotta@cineca.it>
"""

# from flask import request
# from utilities.helpers import get_api_url
# from restapi.confs import PRODUCTION
import os
from utilities.logs import get_logger
from restapi import decorators as decorate
from restapi.exceptions import RestApiException
from utilities import htmlcodes as hcodes
from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from imc.tasks.services.creation_repository import CreationRepository

from restapi.flask_ext.flask_celery import CeleryExt

logger = get_logger(__name__)


#####################################
class Bulk(GraphBaseOperations):

    allowed_actions = ('import', 'delete')

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
        if req_action == 'import':
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
