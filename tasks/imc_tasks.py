# -*- coding: utf-8 -*-

from __future__ import absolute_import
from ...services.celery import celery_app
from commons.logs import get_logger
import os

log = get_logger(__name__)


####################
# Define your celery tasks

def progress(self, state, info):
    if info is not None:
        log.debug("%s [%s]" % (state, info))
    self.update_state(state=state)


@celery_app.task(bind=True)
def import_file(self, path):
    with celery_app.app.app_context():

        progress(self, 'Starting import', path)

        self.graph = celery_app.get_service('neo4j')

        try:

            # self.fileNode = self.graph.File.nodes.get(accession=accession)

            # METADATA EXTRACTION
            filename, file_extension = os.path.splitext(path)

            if file_extension.startswith("."):
                file_extension = file_extension[1:]

            progress(self, 'Extracting metadata', path)
            import codecs
            # with codecs.open(path, 'r', encoding='utf8') as f:
            with codecs.open(path, 'r', encoding='latin-1') as f:
                while True:
                    line = f.readline()
                    if not line:
                        break
                    # print(line)
                    log.info(line.strip())

            # SAVE METADATA
            # self.fileNode.status = 'completed'
            # self.fileNode.metadata = metadata
            # self.fileNode.save()

            progress(self, 'Completed', path)

        # except self.graph.File.DoesNotExist:
        #     progress(self, 'Import error', None)
        #     log.error("Task error, path %s not found" % path)
        except Exception as e:
            progress(self, 'Import error', None)
            log.error("Task error, %s" % e)
            raise e

        return 1
