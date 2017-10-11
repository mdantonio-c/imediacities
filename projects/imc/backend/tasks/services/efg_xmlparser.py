import xml.etree.ElementTree as ET
from xml.dom import minidom
from imc.models import codelists
from utilities.logs import get_logger

log = get_logger(__name__)


class EFG_XMLParser():

    ns = {'efg': 'http://www.europeanfilmgateway.eu/efg'}

    def __init__(self):
        self.warnings = []

    def get_root(self, filepath):
        tree = ET.parse(filepath)
        return tree.getroot()

    def get_creation_ref(self, filepath):
        root = ET.parse(filepath)
        record = root.find('efg:avcreation', self.ns)
        if record is not None:
            nodes = record.findall(
                './efg:avManifestation/efg:recordSource/efg:sourceID', self.ns)
            if len(nodes) <= 0:
                return None
            return nodes[0].text
        record = root.find('efg:nonavcreation', self.ns)
        if record is not None:
            nodes = record.findall(
                './efg:nonAVManifestation/efg:recordSource/efg:sourceID', self.ns)
            if len(nodes) <= 0:
                return None
            return nodes[0].text

    def get_creation_type(self, filepath):
        """
        Assume Video for avcreation and Image for nonavcreation.
        """
        root = ET.parse(filepath)
        if root.find('efg:avcreation', self.ns) is not None:
            return dict(codelists.CONTENT_TYPES)['Video']
        if root.find('efg:nonavcreation', self.ns) is not None:
            return dict(codelists.CONTENT_TYPES)['Image']

    def get_av_creations(self, filepath):
        root = ET.parse(filepath)
        return root.findall("./efg:avcreation", self.ns)

    def get_av_creation_by_ref(self, filepath, ref_id):
        root = ET.parse(filepath)
        nodes = root.findall(
            "./efg:avcreation/efg:avManifestation/efg:recordSource/[efg:sourceID='" +
            ref_id + "']/../..", self.ns)
        if len(nodes) <= 0:
            return None
        return nodes[0]

    def get_creation_by_type(self, filepath, item_type):
        root = ET.parse(filepath)
        if item_type == 'Video':
            return root.find('efg:avcreation', self.ns)
        elif item_type == 'Image':
            return root.find('efg:nonavcreation', self.ns)
        else:
            raise ValueError("Invalid item type for " + item_type)

    def get_non_av_creations(self, filepath):
        root = ET.parse(filepath)
        return root.findall("./efg:nonavcreation", self.ns)

    def get_identifying_title(self, record):
        """
        Returns identifying_title, identifying_title_origin
        """
        title_el = record.find("./efg:identifyingTitle", self.ns)
        if title_el is not None:
            return title_el.text, title_el.get('origin')

        log.debug(
            'Identifying Title not found... look at the first Title composite')
        nodes = record.findall("./efg:title[1]/efg:text", self.ns)
        if len(nodes) <= 0:
            raise ValueError("Identifying title is missing")
        return nodes[0].text, None

    def get_production_years(self, record):
        production_years = set()
        nodes = record.findall("./efg:productionYear", self.ns)
        if len(nodes) <= 0:
            raise ValueError("Production year is missing")
        for n in nodes:
            production_years.add(n.text)
        return list(production_years)

    def get_rights_status(self, record, audio_visual=False):
        inpath = 'efg:avManifestation' if audio_visual else 'efg:nonAVManifestation'
        node = record.find("./" + inpath + "/efg:rightsStatus", self.ns)
        if node is None:
            raise ValueError("Rights status is missing")
        code_el = codelists.fromDescription(node.text, codelists.RIGHTS_STATUS)
        if code_el is None:
            raise ValueError(
                'Invalid rights status description for: ' + node.text)
        return code_el[0]

    def get_view_filmography(self, record):
        nodes = record.findall("./efg:viewFilmography", self.ns)
        if len(nodes) <= 0:
            return None
        res = set()
        for node in nodes:
            res.add(node.text)
        return list(res)

    def parse_record_sources(self, record, audio_visual=False):
        """
        Returns a list of sources in the form of:
        [[<recordsource 'dict'>, <provider 'dict'>], etc.]
        """
        record_sources = []
        bind_url = False
        inpath = 'efg:avManifestation' if audio_visual else 'efg:nonAVManifestation'
        for node in record.findall("./" + inpath + "/efg:recordSource", self.ns):
            rs = {}
            rs['source_id'] = node.find('efg:sourceID', self.ns).text
            log.debug('record source [ID]: %s' % rs['source_id'])

            # record provider
            provider = {}
            provider_el = node.find('efg:provider', self.ns)
            provider['name'] = provider_el.text
            provider['identifier'] = provider_el.get('id')
            p_scheme = provider_el.get('schemeID')
            scheme = codelists.fromDescription(
                p_scheme, codelists.PROVIDER_SCHEMES)
            if scheme is None:
                raise ValueError(
                    'Invalid provider scheme value for [%s]' % p_scheme)
            provider['scheme'] = scheme[0]
            log.debug('Record Provider: {}'.format(provider))

            # bind here the url only to the first element
            # this is a naive solution but enough because we expect here ONLY
            # one record_source (that of the archive)
            if not bind_url:
                rs['is_shown_at'] = self.get_record_source_url(
                    record, audio_visual)
                bind_url = True
            record_sources.append([rs, provider])
        return record_sources

    def get_record_source(self, record, audio_visual=False):
        """
        Naive implementation to get always the first record source as the
        archive one.
        """
        return self.parse_record_sources(record, audio_visual)[0]

    def get_record_source_url(self, record, audio_visual=False):
        """
        Return the url of the source provider where the content is shown.
        """
        inpath = 'efg:avManifestation' if audio_visual else 'efg:nonAVManifestation'
        node = record.find('./' + inpath + '[1]/efg:item[1]/efg:isShownAt', self.ns)
        if node is not None:
            return node.text

    def parse_titles(self, record, avcreation=False):
        titles = []
        for node in record.findall("efg:title", self.ns):
            title = {}
            lang = node.get('lang')
            if lang is not None and lang.lower() != 'n/a':
                lang_val = lang.lower()
                lang_code = codelists.fromCode(lang_val, codelists.LANGUAGE)
                if lang_code is None:
                    self.warnings.append(
                        'Invalid title language for: ' + lang.text)
                else:
                    title['language'] = lang_code[0]
            if avcreation:
                parts = []
                for part in node.findall('efg:partDesignation', self.ns):
                    part_unit = part.find('efg:unit', self.ns).text
                    code_el = codelists.fromCode(
                        part_unit, codelists.AV_TITLE_UNIT)
                    if code_el is None:
                        raise ValueError(
                            'Invalid part designation unit for: ' + part_unit)
                    parts.append("{} {}".format(
                        code_el[0], part.find('efg:value', self.ns).text))
                title['part_designations'] = parts
            title['text'] = node.find('efg:text', self.ns).text
            title_rel = node.find('efg:relation', self.ns)
            if title_rel is not None and title_rel.text.lower() != 'n/a':
                code_el = codelists.fromCode(
                    title_rel.text, codelists.AV_TITLE_TYPES)
                if code_el is None:
                    self.warnings.append(
                        'Invalid title type for: ' + title_rel.text)
                else:
                    title['relation'] = code_el[0]
            log.debug('title: {}'.format(title))
            titles.append(title)
        return titles

    def parse_keywords(self, record):
        keywords = []
        for node in record.findall("efg:keywords", self.ns):
            for term in node.findall('efg:term', self.ns):
                keyword = {}
                ktype = node.get('type')
                if ktype is not None and ktype.lower() != 'n/a':
                    # filter ktype with value 'Project'
                    if ktype == 'Project':
                        continue
                    code_el = codelists.fromDescription(
                        ktype, codelists.KEYWORD_TYPES)
                    if code_el is None:
                        self.warnings.append(
                            'Invalid keyword type for: ' + ktype)
                    else:
                        keyword['keyword_type'] = code_el[0]
                        log.debug('keyword [type]: %s' % keyword['keyword_type'])
                lang = node.get('lang')
                if lang is not None and lang.lower() != 'n/a':
                    lang_val = lang.lower()
                    lang_code = codelists.fromCode(lang_val, codelists.LANGUAGE)
                    if lang_code is None:
                        self.warnings.append(
                            'Invalid keyword language for: ' + lang.text)
                    else:
                        keyword['language'] = lang_code[0]
                if ktype == 'Form':
                    # check term from a controlled IMC list
                    if term.text.lower() == 'n/a':
                        continue
                    code_el = codelists.fromCode(
                        term.text, codelists.FORM)
                    if code_el is None:
                        self.warnings.append('Invalid form type for: ' + term.text)
                        continue
                    else:
                        keyword['term'] = code_el[0]
                else:
                    keyword['term'] = term.text
                log.debug('keyword: {} | {}'.format(
                    keyword['language'], keyword['term']))
                keyword['termID'] = term.get('id')
                keyword['schemeID'] = node.get('scheme')
                keywords.append(keyword)
        return keywords

    def parse_descriptions(self, record):
        descriptions = []
        for node in record.findall("efg:description", self.ns):
            description = {}
            dtype = node.get('type')
            if dtype is not None and dtype.lower() != 'n/a':
                code_el = codelists.fromDescription(
                    dtype, codelists.DESCRIPTION_TYPES)
                if code_el is None:
                    self.warnings.append(
                        'Invalid description type for: ' + dtype)
                else:
                    description['description_type'] = code_el[0]
            lang = node.get('lang')
            if lang is not None and lang.lower() != 'n/a':
                lang_val = lang.lower()
                lang_code = codelists.fromCode(lang_val, codelists.LANGUAGE)
                if lang_code is None:
                    self.warnings.append(
                        'Invalid description language for: ' + lang)
                else:
                    description['language'] = lang_code[0]
            description['source_ref'] = node.get('source')
            description['text'] = node.text
            log.debug('description: {}'.format(description))
            descriptions.append(description)
        if len(descriptions) == 0:
            raise ValueError('Description is missing')
        return descriptions

    def parse_coverages(self, record, audio_visual=False):
        inpath = 'efg:avManifestation' if audio_visual else 'efg:nonAVManifestation'
        coverages = []
        for node in record.findall("./" + inpath + "/efg:coverage", self.ns):
            c = {}
            c['spatial'] = []
            c['temporal'] = []
            for s in node.findall('efg:spatial', self.ns):
                log.debug('spatial: %s' % s.text)
                c['spatial'].append(s.text)
            for t in node.findall('efg:temporal', self.ns):
                log.debug('temporal: %s' % t.text)
                c['temporal'].append(t.text)
            coverages.append(c)
        return coverages

    def parse_languages(self, record, audio_visual=False):
        """
        Extract language and usage if any. It returns an array of arrays as in
        the following example:
        [['fr','03'],['fr','25'],['ca','25']]
        The second nested element corresponds to the usage code in the
        controlled codelist.
        """
        inpath = 'efg:avManifestation' if audio_visual else 'efg:nonAVManifestation'
        languages = []
        for node in record.findall("./" + inpath + "/efg:language", self.ns):
            lang = node.text.lower()
            if lang.lower() == 'n/a':
                continue
            lang_code = codelists.fromCode(lang, codelists.LANGUAGE)
            if lang_code is None:
                self.warnings.append('Invalid language for: ' + node.text)
                continue
            else:
                lang = lang_code[0]

            usage = node.get('usage')
            if usage is not None:
                if usage.lower() == 'n/a':
                    usage = None
                else:
                    code_el = codelists.fromDescription(
                        usage, codelists.LANGUAGE_USAGES)
                    if code_el is None:
                        self.warnings.append(
                            'Invalid language usage for: ' + usage)
                        usage = None
                    else:
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
        for node in record.findall("./efg:countryOfReference", self.ns):
            country = node.text.upper()
            if codelists.fromCode(country, codelists.COUNTRY) is None:
                self.warnings.append(
                    'Invalid country code for: ' + node.text)
                continue
            reference = node.get('reference')
            country_reference = [country, reference]
            log.debug("country: {}, reference: {}"
                      .format(country_reference[0], country_reference[1]))
            countries.append(country_reference)
        return countries

    def parse_video_format(self, record):
        """
        Extract format info from av entity and returns a VideoFormat props.
        """
        node = record.find('./efg:avManifestation/efg:format', self.ns)
        if node is not None:
            video_format = {}
            # gauge (0..1) enum
            gauge_el = node.find('efg:gauge', self.ns)
            if gauge_el is not None and gauge_el.text.lower() != 'n/a':
                code_el = codelists.fromCode(
                    gauge_el.text, codelists.GAUGE)
                if code_el is None:
                    self.warnings.append(
                        'Invalid gauge for: ' + gauge_el.text)
                else:
                    video_format['gauge'] = code_el[0]
            # aspectRation (0..1) enum
            aspect_ratio_el = node.find('efg:aspectRatio', self.ns)
            if aspect_ratio_el is not None and aspect_ratio_el.text.lower() != 'n/a':
                code_el = codelists.fromCode(
                    aspect_ratio_el.text, codelists.ASPECT_RATIO)
                if code_el is None:
                    self.warnings.append(
                        'Invalid aspect ratio for: ' + aspect_ratio_el.text)
                else:
                    video_format['aspect_ratio'] = code_el[0]
            # sound (0..1) enum
            sound_el = node.find('efg:sound', self.ns)
            if sound_el is not None:
                code_el = codelists.fromDescription(
                    sound_el.text, codelists.VIDEO_SOUND)
                if code_el is None:
                    self.warnings.append(
                        'Invalid format sound for: ' + sound_el.text)
                else:
                    video_format['sound'] = code_el[0]
            # colour (0..1)
            colour_el = node.find('efg:colour', self.ns)
            if colour_el is not None and colour_el.text.lower() != 'n/a':
                code_el = codelists.fromDescription(
                    colour_el.text, codelists.COLOUR)
                if code_el is None:
                    self.warnings.append(
                        'Invalid format colour for: ' + colour_el.text)
                else:
                    video_format['colour'] = code_el[0]
            log.debug(video_format)
            return video_format

    def get_collection_title(self, record):
        """
        Extract the collection title, if any, from relCollection/title
        """
        node = record.find('./efg:relCollection[1]/efg:title', self.ns)
        if node is not None:
            return node.text

    def parse_related_agents(self, record):
        """
        Extract related agents as a list of Agent props with their related
        contribution activities in the creation.
        e.g. [[<type 'dict'>, ['Director', 'Screenplay']], etc.]
        """
        nodes = []
        persons = record.findall('./efg:relPerson', self.ns)
        if len(persons) > 0:
            nodes.extend(persons)
        corporates = record.findall('./efg:relCorporate', self.ns)
        if len(corporates) > 0:
            nodes.extend(corporates)

        agents = []
        for agent_node in nodes:
            props = {}
            props['names'] = [agent_node.find('efg:name', self.ns).text]
            activities = []
            rel_agent_type = agent_node.find('efg:type', self.ns)
            if rel_agent_type is not None and rel_agent_type.text.lower() != 'n/a':
                code_el = codelists.fromDescription(
                    rel_agent_type.text, codelists.TYPE_OF_ACTIVITY)
                if code_el is None:
                    self.warnings.append(
                        'Invalid agent activity for: ' + rel_agent_type.text)
                else:
                    activities.append(rel_agent_type.text)

            if agent_node.tag == 'relPerson' or 'efg:relPerson':
                props['agent_type'] = 'P'
            elif agent_node.tag == 'relCorporate' or 'efg:relCorporate':
                props['agent_type'] = 'C'
            else:
                # should never be reached
                raise ValueError(
                    'Invalid tag name for: {}'.format(agent_node.tag))

            agent = None
            # de-duplicate agents
            for item in agents:
                if props['names'][0] in item[0]['names']:
                    log.debug('FOUND agent: ' + props['names'][0])
                    agent = item[0]
                    item[1].extend(activities)
                    log.debug('added activities: {}'.format(activities))
                    break
            if agent is None:
                agents.append([props, activities])

        log.debug(agent.names[0] for agent in agents)
        return agents

    def parse_identifiers(self, record):
        ids = []
        for identifier in record.findall('./efg:identifier', self.ns):
            scheme = ''
            if identifier.get('scheme') is not None:
                scheme = identifier.get('scheme').upper()
            ids.append(scheme + ':' + identifier.text)
        return ids

    def parse_rightholders(self, record, audio_visual=False):
        inpath = 'efg:avManifestation' if audio_visual else 'efg:nonAVManifestation'
        rightholders = []
        for rightholder in record.findall('./' + inpath + '/efg:rightsHolder', self.ns):
            r = {'name': rightholder.text}
            url = rightholder.get('URL')
            if url is not None:
                r['url'] = url
            rightholders.append(r)
        return rightholders

    def get_provenance(self, record, audio_visual=False):
        inpath = 'efg:avManifestation' if audio_visual else 'efg:nonAVManifestation'
        node = record.find('./' + inpath + '/efg:provenance', self.ns)
        if node is not None:
            return node.text

    def get_non_av_type(self, record):
        node = record.find('./efg:nonAVManifestation/efg:type', self.ns)
        if node is None:
            raise ValueError('Non AV type is missing')
        value = node.text
        code_el = codelists.fromCode(
            value, codelists.NON_AV_TYPES)
        if code_el is None:
            raise ValueError('Invalid Non-AV type for: ' + value)
        return code_el[0]

    def get_non_av_specific_type(self, record):
        node = record.find('./efg:nonAVManifestation/efg:specificType', self.ns)
        if node is None:
            raise ValueError('Non-AV specific type is missing')
        code_el = codelists.fromDescription(
            node.text, codelists.NON_AV_SPECIFIC_TYPES)
        if code_el is None:
            raise ValueError('Invalid Non-AV spefic type for: ' + node.text)
        return code_el[0]

    def get_physical_format_size(self, record):
        """
        Return an array with 2 element as follow:
        ["5x5", "pixel"]
        """
        node = record.find(
            './efg:nonAVManifestation/efg:physicalFormat', self.ns)
        if node is not None:
            value = node.text
            unit = node.get('size')
            return [value, unit]

    def get_date_created(self, record):
        dates = []
        for date in record.findall('efg:dateCreated', self.ns):
            dates.append(date.text)
        if len(dates) == 0:
            raise ValueError("Expected at least one dateCreated")
        return dates

    def get_colour(self, record):
        node = record.find('./efg:nonAVManifestation/efg:colour', self.ns)
        if node is not None:
            code_el = codelists.fromDescription(node.text, codelists.COLOUR)
            if code_el is not None:
                return code_el[0]
            self.warnings.append(
                'Invalid format colour for: ' + code_el.text)

    def __parse_creation(self, record, audio_visual=False):
        properties = {}
        properties['external_ids'] = self.parse_identifiers(record)
        properties['rights_status'] = self.get_rights_status(
            record, audio_visual)
        properties['collection_title'] = self.get_collection_title(record)
        # provenance is determined by the group from IS_OWNED_BY relationship,
        # ignore it!
        # properties['provenance'] = self.get_provenance(record, audio_visual)

        relationships = {}
        relationships['record_sources'] = self.parse_record_sources(
            record, audio_visual)
        relationships['titles'] = self.parse_titles(
            record, avcreation=audio_visual)
        relationships['keywords'] = self.parse_keywords(record)
        relationships['descriptions'] = self.parse_descriptions(record)
        relationships['languages'] = self.parse_languages(record, audio_visual)
        relationships['coverages'] = self.parse_coverages(record, audio_visual)
        relationships['rightholders'] = self.parse_rightholders(
            record, audio_visual)

        # agents
        relationships['agents'] = self.parse_related_agents(record)

        return properties, relationships

    def parse_av_creation(self, record):
        log.debug("--- parsing AV Entity ---")
        av_creation = {}

        properties, relationships = self.__parse_creation(
            record, audio_visual=True)

        # manage av properties
        properties['identifying_title'], \
            properties['identifying_title_origin'] = self.get_identifying_title(
                record)
        properties['production_years'] = self.get_production_years(record)
        properties['view_filmography'] = self.get_view_filmography(record)
        av_creation['properties'] = properties

        # manage av relationships
        relationships['production_countries'] = self.parse_production_contries(
            record)
        relationships['video_format'] = self.parse_video_format(record)
        av_creation['relationships'] = relationships
        if len(self.warnings) > 0:
            log.warning(
                "Creation parsed with {} warning(s)".format(len(self.warnings)))
        return av_creation

    def parse_non_av_creation(self, record):
        log.debug("--- parsing NON AV Entity ---")
        non_av_creation = {}

        properties, relationships = self.__parse_creation(record)

        # manage non_av properties
        properties['non_av_type'] = self.get_non_av_type(record)
        properties['specific_type'] = self.get_non_av_specific_type(record)
        properties['phisical_format_size'] = self.get_physical_format_size(
            record)
        properties['date_created'] = self.get_date_created(record)
        properties['colour'] = self.get_colour(record)
        non_av_creation['properties'] = properties

        # manage non_av relationships
        non_av_creation['relationships'] = relationships
        if len(self.warnings) > 0:
            log.warning(
                "Creation parsed with {} warning(s)".format(len(self.warnings)))
        return non_av_creation

    def prettify(elem):
        """Return a pretty-printed XML string for the Element."""
        rough_string = ET.tostring(elem, 'utf-8')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
