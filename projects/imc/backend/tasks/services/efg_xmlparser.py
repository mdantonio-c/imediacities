import xml.etree.ElementTree as ET
from xml.dom import minidom
from imc.models.neo4j import (
    RecordSource, Title, Keyword, Description, Coverage, VideoFormat, Agent,
    Provider, Rightholder
)
from imc.models import codelists
from utilities.logs import get_logger

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
        """
        Returns identifying_title, identifying_title_origin
        """
        title_el = record.find("./identifyingTitle")
        if title_el is not None:
            return title_el.text, title_el.get('origin')

        log.debug(
            'Identifying Title not found... look at the first Title composite')
        nodes = record.findall("./title[1]/text")
        if len(nodes) <= 0:
            return None, None
        return nodes[0].text, None

    def get_production_years(self, record):
        production_years = set()
        nodes = record.findall("./productionYear")
        for n in nodes:
            production_years.add(n.text)
        return list(production_years)

    def get_rights_status(self, record):
        node = record.find("./avManifestation/rightsStatus")
        if node is None:
            raise ValueError("Rights status is missing")
        code_el = codelists.fromDescription(node.text, codelists.RIGHTS_STATUS)
        if code_el is None:
            raise ValueError('Invalid rights status description for: ' + node.text)
        return code_el[0]

    def get_view_filmography(self, record):
        nodes = record.findall("./viewFilmography")
        if len(nodes) <= 0:
            return None
        res = set()
        for node in nodes:
            res.add(node.text)
        return list(res)

    def parse_record_sources(self, record):
        """
        Returns a list of sources in the form of:
        [[<RecordSource>, <Provider>], etc.]
        """
        record_sources = []
        bind_url = False
        for node in record.findall("./avManifestation/recordSource"):
            rs = RecordSource()
            rs.source_id = node.find('sourceID').text
            log.debug('record source [ID]: %s' % rs.source_id)

            # record provider
            provider = Provider()
            provider_el = node.find('provider')
            provider.name = provider_el.text
            provider.identifier = provider_el.get('id')
            p_scheme = provider_el.get('schemeID')
            scheme = codelists.fromDescription(
                p_scheme, codelists.PROVIDER_SCHEMES)
            if scheme is None:
                raise ValueError(
                    'Invalid provider scheme value for [%s]' % p_scheme)
            provider.scheme = scheme[0]
            log.debug('Record Provider: {}'.format(provider))

            # bind here the url only to the first element
            # this is a naive solution but enough because we expect here ONLY
            # one record_source (that of the archive)
            if not bind_url:
                rs.is_shown_at = self.get_record_source_url(record)
                bind_url = True
            record_sources.append([rs, provider])
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

    def parse_titles(self, record, avcreation=False):
        titles = []
        for node in record.findall("title"):
            title = Title()
            title.language = node.get('lang')
            log.debug('title [lang]: %s' % title.language)
            if avcreation:
                parts = []
                for part in node.iter('partDesignation'):
                    part_unit = part.find('unit').text
                    code_el = codelists.fromCode(
                        part_unit, codelists.AV_TITLE_UNIT)
                    if code_el is None:
                        raise ValueError('Invalid part designation unit for: ' + part_unit)
                    parts.append("{} {}".format(
                        code_el[0], part.find('value').text))
                title.part_designations = parts
            title.text = node.find('text').text
            log.debug('title [text]: %s' % title.text)
            titles.append(title)
        return titles

    def parse_keywords(self, record):
        keywords = []
        for node in record.findall("keywords"):
            for term in node.iter('term'):
                keyword = Keyword()
                ktype = node.get('type')
                if ktype is not None and ktype.lower() != 'n/a':
                    # filter ktype with value 'Project'
                    if ktype == 'Project':
                        continue
                    code_el = codelists.fromDescription(
                        ktype, codelists.KEYWORD_TYPES)
                    if code_el is None:
                        raise ValueError('Invalid keyword type for: ' + usage)
                    keyword.keyword_type = code_el[0]
                    log.debug('keyword [type]: %s' % keyword.keyword_type)
                if node.get('lang') is not None:
                    keyword.language = node.get('lang').lower()
                keyword.term = term.text
                log.debug('keyword: {} | {}'.format(
                    keyword.language, keyword.term))
                keyword.termID = term.get('id')
                keyword.schemeID = node.get('scheme')
                keywords.append(keyword)
        return keywords

    def parse_descriptions(self, record):
        descriptions = []
        for node in record.findall("description"):
            description = Description()
            dtype = node.get('type')
            if dtype is not None:
                code_el = codelists.fromDescription(
                    dtype, codelists.DESCRIPTION_TYPES)
                if code_el is None:
                    raise ValueError('Invalid description type for: ' + usage)
                description.description_type = code_el[0]
                log.debug('description [type]: %s' % description.description_type)
            description.language = node.get('lang')
            log.debug('description [lang]: %s' % description.language)
            description.source_ref = node.get('source')
            log.debug('description [source]: %s' % description.source_ref)
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

    def parse_languages(self, record):
        """
        Extract language and usage if any. It returns an array of arrays as in
        the following example:
        [['fr','03'],['fr','25'],['ca','25']]
        The second nested element corresponds to the usage code in the
        controlled codelist.
        """
        languages = []
        for node in record.findall("./avManifestation/language"):
            lang = node.text
            usage = node.get('usage')
            if usage is not None:
                code_el = codelists.fromDescription(
                    usage, codelists.LANGUAGE_USAGES)
                if code_el is None:
                    raise ValueError('Invalid language usage for: ' + usage)
                usage = code_el[0]
            lang_usage = [lang, usage]
            log.debug("lang code: {}, usage code: {}"
                      .format(lang_usage[0], lang_usage[1]))
            languages.append(lang_usage)
        return languages

    def parse_production_contries(self, record):
        """
        Extract country and reference if any.
        """
        countries = []
        for node in record.findall("./countryOfReference"):
            country = node.text
            if codelists.fromCode(country, codelists.COUNTRY) is None:
                raise ValueError('Invalid country code for: ' + country)
            reference = node.get('reference')
            country_reference = [country, reference]
            log.debug("country: {}, reference: {}"
                      .format(country_reference[0], country_reference[1]))
            countries.append(country_reference)
        return countries

    def parse_video_format(self, record):
        """
        Extract format info from av entity and returns a VideoFormat instance.
        """
        node = record.find('./avManifestation/format')
        if node is not None:
            video_format = VideoFormat()
            # gauge (0..1)
            gauge_el = node.find('gauge')
            if gauge_el is not None:
                video_format.gauge = gauge_el.text
            # aspectRation (0..1)
            aspect_ratio_el = node.find('aspectRation')
            if aspect_ratio_el is not None:
                video_format.aspect_ratio = aspect_ratio_el.text
            # sound (0..1) enum
            sound_el = node.find('sound')
            if sound_el is not None:
                code_el = codelists.fromDescription(
                    sound_el.text, codelists.VIDEO_SOUND)
                if code_el is None:
                    raise ValueError('Invalid format sound for: ' + sound_el.text)
                video_format.sound = code_el[0]
            # colour (0..1)
            colour_el = node.find('colour')
            if colour_el is not None:
                code_el = codelists.fromDescription(
                    colour_el.text, codelists.COLOUR)
                if code_el is None:
                    raise ValueError('Invalid format colour for: ' + colour_el.text)
                video_format.colour = code_el[0]
            log.debug(video_format)
            return video_format

    def get_collection_title(self, record):
        """
        Extract the collection title, if any, from relCollection/title
        """
        node = record.find('./relCollection[1]/title')
        if node is not None:
            return node.text

    def parse_related_agents(self, record):
        """
        Extract related agents as a list of Agent instances with their related
        contribution activities in the creation.
        e.g. [[<class Agent>, ['Director', 'Screenplay']], etc.]
        """
        nodes = []
        persons = record.findall('./relPerson')
        if len(persons) > 0:
            nodes.extend(persons)
        corporates = record.findall('./relCorporate')
        if len(corporates) > 0:
            nodes.extend(corporates)

        agents = []
        for agent_node in nodes:
            props = {}
            props['names'] = [agent_node.find('name').text]
            activities = []
            rel_agent_type = agent_node.find('type')
            if rel_agent_type is not None:
                activities.append(rel_agent_type.text)

            if agent_node.tag == 'relPerson':
                props['agent_type'] = 'P'
            elif agent_node.tag == 'relCorporate':
                props['agent_type'] = 'P'
            else:
                # should never be reached
                raise ValueError(
                    'Invalid tag name for: '.format(agent_node.tag))

            agent = None
            # de-duplicate agents
            for item in agents:
                if props['names'][0] in item[0].names:
                    log.debug('FOUND agent: ' + props['names'][0])
                    agent = item[0]
                    item[1].extend(activities)
                    log.debug('added activities: {}'.format(activities))
                    break
            if agent is None:
                agent = Agent(**props)
                agents.append([agent, activities])

        log.debug(agent.names[0] for agent in agents)
        return agents

    def parse_identifiers(self, record):
        ids = []
        for identifier in record.findall('./identifier'):
            scheme = ''
            if identifier.get('scheme') is not None:
                scheme = identifier.get('scheme').upper()
            ids.append(scheme + ':' + identifier.text)
        return ids

    def parse_rightholders(self, record):
        rightholders = []
        for rightholder in record.findall('./avManifestation/rightsHolder'):
            r = Rightholder(name2=rightholder.text)
            url = rightholder.get('URL')
            if url is not None:
                r.url = url
            rightholders.append(r)
        return rightholders

    def __parse_creation(self, record, audio_visual=False):
        properties = {}
        properties['external_ids'] = self.parse_identifiers(record)
        properties['rights_status'] = self.get_rights_status(record)
        properties['collection_title'] = self.get_collection_title(record)

        relationships = {}
        relationships['record_sources'] = self.parse_record_sources(record)
        relationships['titles'] = self.parse_titles(
            record, avcreation=audio_visual)
        relationships['keywords'] = self.parse_keywords(record)
        relationships['descriptions'] = self.parse_descriptions(record)
        relationships['languages'] = self.parse_languages(record)
        relationships['coverages'] = self.parse_coverages(record)
        relationships['rightholders'] = self.parse_rightholders(record)

        # agents
        relationships['agents'] = self.parse_related_agents(record)

        return properties, relationships

    def parse_av_creation(self, record):
        log.debug("--- parsing AV Entity ---")
        av_creation = {}

        properties, relationships = self.__parse_creation(record, audio_visual=True)

        # manage av properties
        properties['identifying_title'], \
            properties['identifying_title_origin'] = self.get_identifying_title(record)
        properties['production_years'] = self.get_production_years(record)
        properties['view_filmography'] = self.get_view_filmography(record)
        av_creation['properties'] = properties

        # manage av relationships
        relationships['production_countries'] = self.parse_production_contries(record)
        relationships['video_format'] = self.parse_video_format(record)
        av_creation['relationships'] = relationships
        return av_creation

    def parse_non_av_creation(self, record):
        log.debug("--- parsing NON AV Entity ---")
        non_av_creation = {}

        properties, relationships = self.__parse_creation(record)

        # manage non_av properties
        # TODO
        non_av_creation['properties'] = properties

        # manage non_av relationships
        # TODO
        non_av_creation['relationships'] = relationships
        return non_av_creation

    def prettify(elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
