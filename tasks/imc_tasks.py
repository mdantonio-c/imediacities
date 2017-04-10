# -*- coding: utf-8 -*-

from restapi.resources.basher import BashCommands
from ...services.celery import celery_app
from commons.logs import get_logger
import os
#from lxml import etree
from .services.EFG_XMLParser import EFG_XMLParser
import xml.etree.ElementTree as ET

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

        resource = None
        try:

            resource = self.graph.Stage.nodes.get(uuid=resource_id)

            # METADATA EXTRACTION
            filename, file_extension = os.path.splitext(path)

            if file_extension.startswith("."):
                file_extension = file_extension[1:]

            video_filename = extract_descriptive_metadata(self, path)
            log.info("Video filename %s", video_filename)
            if (video_filename is None):
                raise Exception("No video match found importing file " + path)

            log.debug('filename [%s], extension [%s]', filename, file_extension)
            progress(self, 'Extracting descriptive metadata', path)
            
            # EXECUTE AUTOMATC TOOLS
            progress(self, 'Executing automatic tools', path)
            params = []
            params.append("/imedia-pipeline-cin/analyze.py")
            params.append(video_filename)
            # bash = BashCommands()
            # try:
            #     output = bash.execute_command(
            #         "python3",
            #         params,
            #         parseException=True
            #     )
            #     log.info(output)

            # except BaseException as e:
            #     log.error(e)
            #     raise(e)

            # SAVE AUTOMATIC ANNOTATIONS
            progress(self, 'Extracting automatic annotations', path)
            # TODO

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
            if resource is not None:
                resource.status = 'ERROR'
                resource.status_message = str(e)
                resource.save()
            #raise e/media/gtrotta/OS/Users/giuseppe/Desktop/progetti/I-MEDIA-CITIES/WP6 - Metadata Modelling/EFG/xsd/efg_3.2.07.xsd

        return 1


def extract_descriptive_metadata(self, path):
    """ 
    Simple metadata ingestion:
      - validate against EFG-XSD schema
      - look for the record with the filename in ref elem
      - bind the model
      - save the model (if an occurrence with the same id already exists, delete the old item?)
      - return the referred video filename
    notes:
      - only EFG xml file allowed
      - lookup at the first occurence of the item in the stage area, ignoring the rest
      - raise exception whenever those conditions are not met
    """
    # import codecs
    # with codecs.open(path, 'r', encoding='utf8') as f:
    # #with codecs.open(path, 'r', encoding='latin-1') as f:
    #     while True:
    #         line = f.readline()
    #         if not line:
    #             break
    #         #log.info(line.strip())

    #e = xml.etree.ElementTree.parse(path).getroot()
    parser = EFG_XMLParser()
    root = parser.getRoot(path)
    #tree = etree.parse(path)
    log.debug(ET.tostring(root, encoding='UTF-8'))


def extract_automatic_annotation(self, path):
    """ """
    #tree = etree.parse(path)
    #log.debug(etree.tostring(tree, pretty_print=True))
    pass