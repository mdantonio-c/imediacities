import xml.etree.ElementTree as ET
from xml.dom import minidom
from imc.models.neo4j import (
    Title, Keyword, Description
)
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


class EFG_XMLParser():

    def get_root(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()

        return root

    def get_av_creations(self, filepath):
        root = ET.parse(filepath)

        # all 'avcreation'
        return root.findall("./avcreation")

    def get_av_creation_by_ref(self, filepath, ref_id):
        root = ET.parse(filepath)
        nodes = root.findall(
            "./avcreation/avManifestation/recordSource/[sourceID='" +
            ref_id + "']/../..")
        if len(nodes) <= 0:
            return None
        return nodes[0]

    def get_non_av_creations(self, filepath):
        root = ET.parse(filepath)

        # all 'nonavcreation'
        return root.findall("./nonavcreation")

    def get_av_creation_ref(self, record):
        nodes = record.findall("./avManifestation/recordSource/sourceID")
        if len(nodes) <= 0:
            return None
        return nodes[0].text

    def get_identifying_title(self, record):
        nodes = record.findall("./title[1]/text")
        if len(nodes) <= 0:
            return None
        return nodes[0].text

    def get_production_years(self, record):
        production_years = []
        nodes = record.findall("./productionYear")
        for n in nodes:
            production_years.append(n.text)
        return production_years

    def parse_titles(self, record):
        titles = []
        for node in record.findall("title"):
            title = Title()
            title.language = node.get('lang')
            log.debug('title [lang]: %s' % title.language)

            title.text = node.find('text').text
            log.debug('title [text]: %s' % title.text)
            titles.append(title)
        return titles

    def parse_keywords(self, record):
        keywords = []
        for node in record.findall("keywords"):
            for term in node.iter('term'):
                keyword = Keyword()
                # FIXME
                # keyword.keyword_type = node.get('type')
                # log.debug('keyword [type]: %s' % keyword.keyword_type)
                keyword.language = node.get('lang')
                log.debug('keyword [lang]: %s' % keyword.language)
                keyword.term = term.text
                log.debug('keyword [term]: %s' % keyword.term)
                keyword.termID = term.get('id')
                if keyword.termID is not None:
                    log.debug('keyword [term-id]: %s' % keyword.termID)
                keywords.append(keyword)
        return keywords

    def parse_descriptions(self, record):
        descriptions = []
        for node in record.findall("description"):
            description = Description()
            # FIXME
            description.description_type = node.get('type')
            log.debug('description [type]: %s' % description.description_type)
            description.language = node.get('lang')
            log.debug('description [lang]: %s' % description.language)
            description.source = node.get('source')
            log.debug('description [source]: %s' % description.source)
            description.text = node.text
            log.debug('description [text]: %s' % description.text)
            descriptions.append(description)
        return descriptions

    def parse_av_creation(self, record):
        log.debug("--- parsing AV Entity ---")
        av_creation = {}

        # properties
        properties = {}
        properties['identifying_title'] = self.get_identifying_title(record)
        properties['production_years'] = self.get_production_years(record)
        av_creation['properties'] = properties

        relationships = {}
        relationships['titles'] = self.parse_titles(record)
        relationships['keywords'] = self.parse_keywords(record)
        relationships['descriptions'] = self.parse_descriptions(record)
        av_creation['relationships'] = relationships

        # rights_status
        # contributor

        return av_creation

    def parse_non_av_creation(self, record):
        pass

    def prettify(elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
