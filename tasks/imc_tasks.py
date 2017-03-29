# -*- coding: utf-8 -*-

from restapi.resources.basher import BashCommands
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
def import_file(self, path, resource_id):
    with celery_app.app.app_context():

        progress(self, 'Starting import', path)

        self.graph = celery_app.get_service('neo4j')

        try:

            resource = self.graph.Stage.nodes.get(uuid=resource_id)

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
                    log.info(line.strip())

            params = []
            params.append("imedia-pipeline-cin/analyze.py")
            bash = BashCommands()
            bash.execute_command("python3", params)

            # SAVE METADATA
            resource.status = 'COMPLETED'
            resource.status_message = 'Nothing to declare'
            resource.save()

            progress(self, 'Completed', path)
            # os.remove(path)

        # except self.graph.File.DoesNotExist:
        #     progress(self, 'Import error', None)
        #     log.error("Task error, path %s not found" % path)
        except Exception as e:
            progress(self, 'Import error', None)
            log.error("Task error, %s" % e)
            resource.status = 'ERROR'
            resource.status_message = str(e)
            resource.save()
            raise e

        return 1
