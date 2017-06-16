import xml.etree.ElementTree as ET
from xml.dom import minidom
from imc.models.neo4j import (
    RecordSource, Title, Keyword, Description, Coverage
)
from imc.models import codelists
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

    def get_rights_status(self, record):
        node = record.find("./avManifestation/rightsStatus")
        if node is not None:
            return node.text

    def parse_record_sources(self, record):
        record_sources = []
        bind_url = False
        for node in record.findall("./avManifestation/recordSource"):
            rs = RecordSource()
            rs.source_id = node.find('sourceID').text
            log.debug('record source [ID]: %s' % rs.source_id)
            provider = node.find('provider')
            rs.provider_name = provider.text
            log.debug('record source [provider name]: %s' % rs.provider_name)
            rs.provider_id = provider.get('id')
            log.debug('record source [provider id]: %s' % rs.provider_id)
            p_scheme = provider.get('schemeID')
            for schemes in codelists.PROVIDER_SCHEMES:
                if schemes[1] == p_scheme:
                    rs.provider_scheme = schemes[0]
            log.debug('record source [provider scheme]: %s' %
                      rs.provider_scheme)
            if rs.provider_scheme is None:
                raise ValueError(
                    'Invalid provider scheme value for [%s]' % p_scheme)
            # bind here the url only to the first element
            # this is a naive solution but enough because we expect here ONLY
            # one record_source (the archive one)
            if not bind_url:
                rs.is_shown_at = self.get_record_source_url(record)
                bind_url = True
            record_sources.append(rs)
        return record_sources

    def get_record_source(self, record):
        '''
        Naive implementation to get always the first record source as the
        archive one.
        '''
        return self.parse_record_sources(record)[0]

    def get_record_source_url(self, record):
        '''
        Return the url of the source provider where the content is shown.
        '''
        node = record.find('./avManifestation[1]/item[1]/isShownAt')
        if node is not None:
            return node.text

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
            # description.description_type = node.get('type')
            # log.debug(
            #     'description [type]: %s' % description.description_type)
            description.language = node.get('lang')
            log.debug('description [lang]: %s' % description.language)
            description.source = node.get('source')
            log.debug('description [source]: %s' % description.source)
            description.text = node.text
            log.debug('description [text]: %s' % description.text)
            descriptions.append(description)
        return descriptions

    def parse_coverages(self, record):
        coverages = []
        for node in record.findall("./avManifestation/coverage"):
            c = Coverage()
            c.spatial = []
            c.temporal = []
            for s in node.iter('spatial'):
                log.debug('spatial: %s' % s.text)
                c.spatial.append(s.text)
            for t in node.iter('temporal'):
                log.debug('temporal: %s' % t.text)
                c.temporal.append(t.text)
            coverages.append(c)
        return coverages

    def parse_av_creation(self, record):
        log.debug("--- parsing AV Entity ---")
        av_creation = {}

        # properties
        properties = {}
        properties['identifying_title'] = self.get_identifying_title(record)
        properties['production_years'] = self.get_production_years(record)
        status = self.get_rights_status(record)
        if status is not None and status in codelists.IPR_STATUS:
            properties['rights_status'] = status
        properties['rights_status'] = self.get_rights_status(record)
        av_creation['properties'] = properties

        relationships = {}
        relationships['record_sources'] = self.parse_record_sources(record)
        relationships['titles'] = self.parse_titles(record)
        relationships['keywords'] = self.parse_keywords(record)
        relationships['descriptions'] = self.parse_descriptions(record)
        relationships['coverages'] = self.parse_coverages(record)
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
