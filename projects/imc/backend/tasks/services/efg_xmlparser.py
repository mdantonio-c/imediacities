from datetime import date
from datetime import datetime as dt
from typing import Any, Dict, List, Optional, Tuple
from xml.dom import minidom
from xml.etree import ElementTree as ET

from imc.models import codelists
from restapi.utilities.logs import log


def is_blank(my_string: Optional[str]) -> bool:
    return not (my_string and str(my_string).strip())


def get_text(text_node: Optional[ET.Element]) -> Optional[str]:
    """Return stripped text from node. None otherwise."""
    if text_node is None:
        return None
    if not text_node.text:
        return None
    return text_node.text.strip()


class EFG_XMLParser:

    ns = {"efg": "http://www.europeanfilmgateway.eu/efg"}

    def __init__(self):
        self.warnings = []

    def get_root(self, filepath):
        tree = ET.parse(filepath)
        return tree.getroot()

    def get_creation_ref(self, filepath):
        root = ET.parse(filepath)
        record = root.find("efg:avcreation", self.ns)
        if record is not None:
            nodes = record.findall("./efg:recordSource/efg:sourceID", self.ns)
            if len(nodes) <= 0:
                return None
            return nodes[0].text.strip()  # type: ignore
        record = root.find("efg:nonavcreation", self.ns)
        if record is not None:
            nodes = record.findall("./efg:recordSource/efg:sourceID", self.ns)
            if len(nodes) <= 0:
                return None
            return nodes[0].text.strip()  # type: ignore

    def get_creation_type(self, filepath: str) -> Optional[str]:
        """
        Assume Video for avcreation and Image for nonavcreation.
        """
        root = ET.parse(filepath)
        creation_type = None
        if root.find("efg:avcreation", self.ns) is not None:
            creation_type = dict(codelists.CONTENT_TYPES)["Video"]
        if (
            type_el := root.find(
                "./efg:nonavcreation/efg:nonAVManifestation/efg:type", self.ns
            )

        ) is not None and type_el.text:
            type_value = type_el.text.strip().title()
            creation_type = dict(codelists.CONTENT_TYPES)[type_value]
        return creation_type

    def get_av_creations(self, filepath):
        root = ET.parse(filepath)
        return root.findall("./efg:avcreation", self.ns)

    def get_av_creation_by_ref(self, filepath, ref_id):
        root = ET.parse(filepath)
        nodes = root.findall(
            "./efg:avcreation/efg:recordSource/[efg:sourceID='" + ref_id + "']/..",
            self.ns,
        )
        if len(nodes) <= 0:
            return None
        return nodes[0]

    def get_creation_by_type(self, filepath, item_type):
        root = ET.parse(filepath)
        if item_type == "Video":
            return root.find("efg:avcreation", self.ns)
        elif item_type == "Image" or item_type == "3D-Model":
            return root.find("efg:nonavcreation", self.ns)
        else:
            raise ValueError("Invalid item type for " + item_type)

    def get_non_av_creations(self, filepath):
        root = ET.parse(filepath)
        return root.findall("./efg:nonavcreation", self.ns)

    def get_identifying_title(self, record: ET.Element) -> Tuple[str, Optional[str]]:
        """
        Returns identifying_title, identifying_title_origin
        """
        title_el = record.find("./efg:identifyingTitle", self.ns)
        if title_el and title_el.text:
            return title_el.text.strip(), title_el.get("origin")

        log.debug("Identifying Title not found... look at the first Title composite")
        nodes = record.findall("./efg:title[1]/efg:text", self.ns)
        if not nodes or not nodes[0].text:
            raise ValueError("Identifying title is missing")
        return nodes[0].text.strip(), None

    def get_production_years(self, record: ET.Element) -> List[str]:
        production_years = set()
        nodes = record.findall("./efg:productionYear", self.ns)
        if not nodes:
            raise ValueError("Production year is missing")
        for n in nodes:
            if not (n_text := get_text(n)):
                self.warnings.append("Empty production year")
                continue
            production_years.add(n_text)
        if not production_years:
            raise ValueError("Production year is missing")
        return list(production_years)

    def get_date_issued(self, record: ET.Element) -> Optional[date]:
        node = record.find("./efg:date[@type='issued']", self.ns)
        date_issued = None
        if node and node.text:
            try:
                # expected YYYY-MM-DD
                date_time_str = node.text.strip()
                d = dt.strptime(date_time_str, "%Y-%m-%d")
                # Convert datetime object to date object.
                date_issued = d.date()
            except ValueError as e:
                self.warnings.append(f"Invalid 'issued date': {str(e)}")
        return date_issued

    def get_rights_status(self, record: ET.Element, audio_visual: bool = False) -> str:
        in_path = "efg:avManifestation" if audio_visual else "efg:nonAVManifestation"
        rs = get_text(record.find(f"./{in_path}/efg:rightsStatus", self.ns))
        if not rs:
            raise ValueError("Rights status is missing")
        code_el = codelists.fromDescription(rs, codelists.RIGHTS_STATUS)
        if not code_el:
            raise ValueError(f"Invalid rights status description for: {rs}")
        return code_el[0]

    def get_view_filmography(self, record: ET.Element) -> Optional[List[str]]:
        nodes = record.findall("./efg:viewFilmography", self.ns)
        if not nodes:
            return None
        res = set()
        for node in nodes:
            filmography = get_text(node)
            if not filmography:
                self.warnings.append("Empty viewFilmography")
                continue
            res.add(filmography)
        return list(res)

    def parse_record_sources(self, record, audio_visual=False):
        """
        Returns a list of sources in the form of:
        [[<recordsource 'dict'>, <provider 'dict'>], etc.]
        """
        record_sources = []
        bind_url = False
        for node in record.findall("./efg:recordSource", self.ns):
            rs = {"source_id": node.find("efg:sourceID", self.ns).text.strip()}
            log.debug("record source [ID]: {}", rs["source_id"])

            # record provider
            provider = {}
            provider_el = node.find("efg:provider", self.ns)
            provider["name"] = provider_el.text.strip()
            provider["identifier"] = provider_el.get("id").upper()
            p_scheme = provider_el.get("schemeID")
            scheme = codelists.fromDescription(p_scheme, codelists.PROVIDER_SCHEMES)
            if scheme is None:
                raise ValueError(f"Invalid provider scheme value for [{p_scheme}]")
            provider["scheme"] = scheme[0]
            log.debug("Record Provider: {}", provider)

            # bind here the url only to the first element
            # this is a naive solution but enough because we expect here ONLY
            # one record_source (that of the archive)
            if not bind_url:
                rs["is_shown_at"] = self.get_record_source_url(record, audio_visual)
                bind_url = True
            record_sources.append([rs, provider])
        return record_sources

    def get_record_source(self, record, audio_visual=False):
        """
        Naive implementation to get always the first record source as the
        archive one.
        """
        return self.parse_record_sources(record, audio_visual)[0]

    def get_record_source_url(
        self, record: ET.Element, audio_visual: bool = False
    ) -> Optional[str]:
        """
        Return the url of the source provider where the content is shown.
        """
        in_path = "efg:avManifestation" if audio_visual else "efg:nonAVManifestation"
        node = record.find(f"./{in_path}[1]/efg:item[1]/efg:isShownAt", self.ns)
        url = None
        if node and node.text and not is_blank(node.text):
            return node.text.strip()
        return url

    def parse_titles(self, record: ET.Element, av_creation: bool = False) -> List[Any]:
        titles: List[Any] = []
        for node in record.findall("efg:title", self.ns):
            title: Dict[str, Any] = {}
            # TEXT
            if text := get_text(node.find("efg:text", self.ns)):
                title["text"] = text
            else:
                # ignore empty text title
                self.warnings.append("Empty text title")
                continue
            # LANG
            lang = node.get("lang")
            if lang and lang.lower() != "n/a":
                lang_val = lang.lower()
                lang_code = codelists.fromCode(lang_val, codelists.LANGUAGE)
                if lang_code is None:
                    self.warnings.append(f"Invalid title language for: {lang}")
                else:
                    title["language"] = lang_code[0]
            # ONLY for av_creation (?)
            if av_creation:
                parts: List[str] = []
                for part in node.findall("efg:partDesignation", self.ns):
                    # PART UNIT
                    if part_unit := get_text(part.find("efg:unit", self.ns)):
                        code_el = codelists.fromCode(part_unit, codelists.AV_TITLE_UNIT)
                        if not code_el:
                            self.warnings.append(
                                f"Invalid part designation unit for: {part_unit}"
                            )
                            continue
                    else:
                        # ignore empty part unit
                        self.warnings.append("Empty part unit")
                        continue
                    # PART VALUE
                    if not (part_value := get_text(part.find("efg:value", self.ns))):
                        # ignore empty part value
                        self.warnings.append("Empty part value")
                        continue
                    parts.append(f"{code_el[0]} {part_value}")
                title["part_designations"] = parts
            # RELATION
            title_rel = get_text(node.find("efg:relation", self.ns))
            if title_rel and title_rel.lower() != "n/a":
                code_el = codelists.fromCode(title_rel, codelists.AV_TITLE_TYPES)
                if not code_el:
                    self.warnings.append(f"Invalid title type for: {title_rel}")
                else:
                    title["relation"] = code_el[0]
            log.debug("title: {}", title)
            titles.append(title)
        if not titles:
            raise ValueError("Title is missing")
        return titles

    def parse_keywords(self, record):
        keywords = []
        for node in record.findall("efg:keywords", self.ns):
            for term in node.findall("efg:term", self.ns):
                keyword: Dict[str, Optional[Any]] = {}
                ktype = node.get("type")
                if ktype is not None and ktype.lower() != "n/a":
                    # filter ktype with value 'Project'
                    if ktype == "Project":
                        continue
                    code_el = codelists.fromDescription(ktype, codelists.KEYWORD_TYPES)
                    if code_el is None:
                        self.warnings.append("Invalid keyword type for: " + ktype)
                    else:
                        keyword["keyword_type"] = code_el[0]
                        log.debug("keyword [type]: {}", keyword["keyword_type"])
                lang = node.get("lang")
                if lang is not None and lang.lower() != "n/a":
                    lang_val = lang.lower()
                    lang_code = codelists.fromCode(lang_val, codelists.LANGUAGE)
                    if lang_code is None:
                        self.warnings.append(
                            "Invalid keyword language for: " + lang.text
                        )
                    else:
                        keyword["language"] = lang_code[0]
                        log.debug("language: {}", keyword["language"])
                if ktype == "Form":
                    # check term from a controlled IMC list
                    if term.text.lower() == "n/a":
                        continue
                    code_el = codelists.fromCode(term.text.strip(), codelists.FORM)
                    if code_el is None:
                        self.warnings.append(
                            "Invalid form type for: " + term.text.strip()
                        )
                        continue
                    else:
                        keyword["term"] = code_el[0]
                else:
                    keyword["term"] = term.text.strip()

                log.debug("keyword: {}", keyword["term"])

                # log.debug('term id: {}', term.get('id'))
                if term.get("id") is not None:
                    # check keyword term id is integer (keyword term id is optional)
                    try:
                        int(term.get("id"))
                        keyword["termID"] = term.get("id")
                    except Exception:
                        self.warnings.append(
                            "Invalid keyword term id for: "
                            + term.get("id")
                            + ". Expected integer."
                        )
                else:
                    keyword["termID"] = None
                keyword["schemeID"] = node.get("scheme")
                keywords.append(keyword)
        return keywords

    def parse_descriptions(self, record):
        descriptions = []
        for node in record.findall("efg:description", self.ns):
            description = {}
            dtype = node.get("type")
            if dtype is not None and dtype.lower() != "n/a":
                code_el = codelists.fromDescription(dtype, codelists.DESCRIPTION_TYPES)
                if code_el is None:
                    self.warnings.append("Invalid description type for: " + dtype)
                else:
                    description["description_type"] = code_el[0]
            lang = node.get("lang")
            if lang is not None and lang.lower() != "n/a":
                lang_val = lang.lower()
                lang_code = codelists.fromCode(lang_val, codelists.LANGUAGE)
                if lang_code is None:
                    self.warnings.append("Invalid description language for: " + lang)
                else:
                    description["language"] = lang_code[0]
            description["source_ref"] = node.get("source")
            description["text"] = node.text.strip()
            log.debug("description: {}", description)
            descriptions.append(description)
        # october 2018: change: description is optional
        # if len(descriptions) == 0:
        #    raise ValueError('Description is missing')
        return descriptions

    def parse_languages(self, record, audio_visual=False):
        """
        Extract language and usage if any. It returns an array of arrays as in
        the following example:
        [['fr','03'],['fr','25'],['ca','25']]
        The second nested element corresponds to the usage code in the
        controlled codelist.
        """
        inpath = "efg:avManifestation" if audio_visual else "efg:nonAVManifestation"
        languages = []
        for node in record.findall("./" + inpath + "/efg:language", self.ns):
            lang = node.text.lower()
            if lang.lower() == "n/a":
                continue
            lang_code = codelists.fromCode(lang, codelists.LANGUAGE)
            if lang_code is None:
                self.warnings.append("Invalid language for: " + node.text)
                continue
            else:
                lang = lang_code[0]

            usage = node.get("usage")
            if usage is not None:
                if usage.lower() == "n/a":
                    usage = None
                else:
                    code_el = codelists.fromDescription(
                        usage, codelists.LANGUAGE_USAGES
                    )
                    if code_el is None:
                        self.warnings.append("Invalid language usage for: " + usage)
                        usage = None
                    else:
                        usage = code_el[0]
            lang_usage = [lang, usage]
            log.debug(f"lang code: {lang_usage[0]}, usage code: {lang_usage[1]}")
            languages.append(lang_usage)
        return languages

    def parse_coverages(self, record, audio_visual=False):
        in_path = "efg:avManifestation" if audio_visual else "efg:nonAVManifestation"
        coverages: Dict[str, List[Any]] = {
            "spatial": [],
            "temporal": [],
        }
        if coverage := record.find(f"./{in_path}/efg:coverage", self.ns):
            for s in coverage.findall("efg:spatial", self.ns):
                spatial = {
                    "spatial_type": s.get("type", None),
                    "value": s.text.strip(),
                }
                log.debug("spatial: {}", spatial)
                coverages["spatial"].append(spatial)
            for t in coverage.findall("efg:temporal", self.ns):
                temporal = {"value": t.text.strip()}
                log.debug("temporal: {}", temporal)
                coverages["temporal"].append(temporal)
        return coverages

    def parse_production_contries(self, record):
        """
        Extract country and reference if any.
        """
        countries = []
        for node in record.findall("./efg:countryOfReference", self.ns):
            country = node.text.strip().upper()
            if codelists.fromCode(country, codelists.COUNTRY) is None:
                self.warnings.append("Invalid country code for: " + node.text.strip())
                continue
            reference = node.get("reference")
            country_reference = [country, reference]
            log.debug(
                "country: {}, reference: {}".format(
                    country_reference[0], country_reference[1]
                )
            )
            countries.append(country_reference)
        return countries

    def parse_video_format(self, record):
        """
        Extract format info from av entity and returns a VideoFormat props.
        """
        node = record.find("./efg:avManifestation/efg:format", self.ns)
        if node is not None:
            video_format = {}
            # gauge (0..1) enum
            gauge_el = node.find("efg:gauge", self.ns)
            if (
                gauge_el is not None
                and gauge_el.text is not None
                and gauge_el.text.lower() != "n/a"
            ):
                code_el = codelists.fromCode(gauge_el.text.strip(), codelists.GAUGE)
                if code_el is None:
                    self.warnings.append("Invalid gauge for: " + gauge_el.text.strip())
                else:
                    video_format["gauge"] = code_el[0]
            # aspectRation (0..1) enum
            aspect_ratio_el = node.find("efg:aspectRatio", self.ns)
            if (
                aspect_ratio_el is not None
                and aspect_ratio_el.text is not None
                and aspect_ratio_el.text.lower() != "n/a"
            ):
                code_el = codelists.fromCode(
                    aspect_ratio_el.text.strip(), codelists.ASPECT_RATIO
                )
                if code_el is None:
                    self.warnings.append(
                        "Invalid aspect ratio for: " + aspect_ratio_el.text.strip()
                    )
                else:
                    video_format["aspect_ratio"] = code_el[0]
            # sound (0..1) enum
            sound_el = node.find("efg:sound", self.ns)
            if (
                sound_el is not None
                and sound_el.text is not None
                and sound_el.text.lower() != "n/a"
            ):
                code_el = codelists.fromDescription(
                    sound_el.text.strip(), codelists.VIDEO_SOUND
                )
                if code_el is None:
                    self.warnings.append(
                        "Invalid format sound for: " + sound_el.text.strip()
                    )
                else:
                    video_format["sound"] = code_el[0]
            # colour (0..1)
            colour_el = node.find("efg:colour", self.ns)
            if (
                colour_el is not None
                and colour_el.text is not None
                and colour_el.text.lower() != "n/a"
            ):
                code_el = codelists.fromDescription(
                    colour_el.text.strip(), codelists.COLOUR
                )
                if code_el is None:
                    self.warnings.append(
                        "Invalid format colour for: " + colour_el.text.strip()
                    )
                else:
                    video_format["colour"] = code_el[0]
            log.debug(video_format)
            return video_format

    def get_collection_title(self, record):
        """
        Extract the collection title, if any, from relCollection/title
        """
        node = record.find("./efg:relCollection[1]/efg:title", self.ns)
        if node is not None:
            return node.text.strip()

    def parse_related_agents(self, record):
        """
        Extract related agents as a list of Agent props with their related
        contribution activities in the creation.
        e.g. [[<type 'dict'>, ['Director', 'Screenplay']], etc.]
        """
        nodes = []
        persons = record.findall("./efg:relPerson", self.ns)
        if len(persons) > 0:
            nodes.extend(persons)
        corporates = record.findall("./efg:relCorporate", self.ns)
        if len(corporates) > 0:
            nodes.extend(corporates)

        agents: Any = []
        for agent_node in nodes:
            props = {"names": [agent_node.find("efg:name", self.ns).text.strip()]}
            activities = []
            rel_agent_type = agent_node.find("efg:type", self.ns)
            if rel_agent_type is not None and rel_agent_type.text.lower() != "n/a":
                code_el = codelists.fromDescription(
                    rel_agent_type.text.strip(), codelists.TYPE_OF_ACTIVITY
                )
                if code_el is None:
                    self.warnings.append(
                        "Invalid agent activity for: " + rel_agent_type.text.strip()
                    )
                else:
                    activities.append(rel_agent_type.text.strip())

            agent_tag = agent_node.tag.split("}")[1][0:]
            if agent_tag == "relPerson":
                props["agent_type"] = "P"  # type: ignore
            elif agent_tag == "relCorporate":
                props["agent_type"] = "C"  # type: ignore
            else:
                # should never be reached
                raise ValueError(f"Invalid tag name for: '{agent_tag}'")

            agent = None
            # de-duplicate agents
            for item in agents:
                if props["names"][0] in item[0]["names"]:
                    log.debug("FOUND agent: " + props["names"][0])
                    agent = item[0]
                    item[1].extend(activities)
                    log.debug("added activities: {}", activities)
                    break
            if agent is None:
                agents.append([props, activities])

        # log.debug(agent.names[0] for agent in agents)
        return agents

    def parse_identifiers(self, record):
        ids = []
        for identifier in record.findall("./efg:identifier", self.ns):
            scheme = ""
            if identifier.get("scheme") is not None:
                scheme = identifier.get("scheme").upper()
            ids.append(scheme + ":" + identifier.text.strip())
        return ids

    def parse_rightholders(self, record, audio_visual=False):
        inpath = "efg:avManifestation" if audio_visual else "efg:nonAVManifestation"
        rightholders = []
        for rightholder in record.findall("./" + inpath + "/efg:rightsHolder", self.ns):
            r = {"name": rightholder.text.strip()}
            url = rightholder.get("URL")
            if url is not None:
                r["url"] = url
            rightholders.append(r)
        return rightholders

    def get_provenance(self, record, audio_visual=False):
        inpath = "efg:avManifestation" if audio_visual else "efg:nonAVManifestation"
        node = record.find("./" + inpath + "/efg:provenance", self.ns)
        if node is not None:
            return node.text.strip()

    def get_non_av_type(self, record):
        node = record.find("./efg:nonAVManifestation/efg:type", self.ns)
        if node is None:
            raise ValueError("Non AV type is missing")
        value = node.text.strip()
        code_el = codelists.fromCode(value, codelists.NON_AV_TYPES)
        if code_el is None:
            raise ValueError("Invalid Non-AV type for: " + value)
        return code_el[0]

    def get_non_av_specific_type(self, record):
        if node := record.find("./efg:nonAVManifestation/efg:specificType", self.ns):
            code_el = codelists.fromDescription(
                node.text.strip(), codelists.NON_AV_SPECIFIC_TYPES
            )
            if code_el is None:
                raise ValueError(
                    "Invalid Non-AV specific type for: " + node.text.strip()
                )
            return code_el[0]

    def get_digital_format(self, record):
        """Get digital format"""
        node = record.find("./efg:nonAVManifestation/efg:digitalFormat", self.ns)
        if node is not None:
            return {"value": node.text.strip(), "size": node.get("size")}

    def get_physical_format_size(self, record):
        """
        Return an array with 2 element as follow:
        ["5x5", "pixel"]
        """
        node = record.find("./efg:nonAVManifestation/efg:physicalFormat", self.ns)
        if node is not None:
            value = node.text.strip()
            unit = node.get("size")
            return [value, unit]

    def get_date_created(self, record):
        dates = []
        for d in record.findall("efg:dateCreated", self.ns):
            dates.append(d.text.strip())
        return dates

    def __parse_creation(self, record, audio_visual=False):
        properties = {
            "external_ids": self.parse_identifiers(record),
            "rights_status": self.get_rights_status(record, audio_visual),
            "collection_title": self.get_collection_title(record),
            "date_issued": self.get_date_issued(record),
        }
        # provenance is determined by the group from IS_OWNED_BY relationship,
        # ignore it!
        # properties['provenance'] = self.get_provenance(record, audio_visual)

        relationships = {
            "record_sources": self.parse_record_sources(record, audio_visual),
            "titles": self.parse_titles(record, av_creation=audio_visual),
            "keywords": self.parse_keywords(record),
            "descriptions": self.parse_descriptions(record),
            "languages": self.parse_languages(record, audio_visual),
            "coverages": self.parse_coverages(record, audio_visual),
            "rightholders": self.parse_rightholders(record, audio_visual),
            "agents": self.parse_related_agents(record),
        }

        # agents

        return properties, relationships

    def parse_av_creation(self, record):
        log.debug("--- parsing AV Entity ---")
        av_creation = {}

        properties, relationships = self.__parse_creation(record, audio_visual=True)

        # manage av properties
        (
            properties["identifying_title"],
            properties["identifying_title_origin"],
        ) = self.get_identifying_title(record)
        properties["production_years"] = self.get_production_years(record)
        properties["view_filmography"] = self.get_view_filmography(record)
        av_creation["properties"] = properties

        # manage av relationships
        relationships["production_countries"] = self.parse_production_contries(record)
        relationships["video_format"] = self.parse_video_format(record)
        av_creation["relationships"] = relationships
        if len(self.warnings) > 0:
            log.warning("Creation parsed with {} warning(s)", len(self.warnings))
        return av_creation

    def get_colour(self, record):
        node = record.find("./efg:nonAVManifestation/efg:colour", self.ns)
        if node is not None:
            code_el = codelists.fromDescription(node.text.strip(), codelists.COLOUR)
            if code_el is not None:
                return code_el[0]
            self.warnings.append("Invalid format colour for: " + node.text.strip())

    def parse_non_av_creation(self, record):
        log.debug("--- parsing NON AV Entity ---")
        non_av_creation = {}

        properties, relationships = self.__parse_creation(record)

        # manage non_av properties
        properties["non_av_type"] = self.get_non_av_type(record)
        properties["specific_type"] = self.get_non_av_specific_type(record)
        properties["digital_format"] = self.get_digital_format(record)
        properties["phisical_format_size"] = self.get_physical_format_size(record)
        properties["date_created"] = self.get_date_created(record)
        properties["colour"] = self.get_colour(record)
        non_av_creation["properties"] = properties

        # manage non_av relationships
        non_av_creation["relationships"] = relationships
        if properties["non_av_type"] == "3d-model":
            # add 3D Format in the item as relationship
            three_dim_format = self.parse_3d_format(record)
            if three_dim_format is None:
                ValueError("3D format is missing")
            non_av_creation["relationships"]["3d-format"] = three_dim_format
        if len(self.warnings) > 0:
            log.warning("Creation parsed with {} warning(s)", len(self.warnings))
        return non_av_creation

    def prettify(self, elem: ET.Element) -> Any:
        """Return a pretty-printed XML string for the Element."""
        rough_string: str = ET.tostring(elem, "utf-8")
        re_parsed = minidom.parseString(rough_string)
        return re_parsed.toprettyxml(indent="  ")

    def parse_3d_format(self, record):
        """Extract 3D format info from 3d models."""
        three_dim_format: Optional[Dict[str, Any]] = None
        if _3d_format := record.find(
            "./efg:nonAVManifestation/efg:item/efg:_3DFormat", self.ns
        ):
            three_dim_format = {"software_used": []}
            level_of_details = _3d_format.find("efg:levelOfDetails", self.ns)
            if level_of_details is not None:
                upper = level_of_details.get("upper", "")
                three_dim_format[
                    "level_of_details"
                ] = f"{level_of_details.text.strip()}:{upper}"
            resolution = _3d_format.find("efg:resolution", self.ns)
            if resolution is not None:
                three_dim_format["resolution"] = int(resolution.text.strip())
                three_dim_format["resolution_type"] = resolution.get("type")
            for sfw in _3d_format.findall("efg:softwareUsed", self.ns):
                three_dim_format["software_used"].append(sfw.text.strip())
            if len(three_dim_format["software_used"]) == 0:
                raise ValueError("Missing software used in 3D format")
            materials = _3d_format.find("efg:materials", self.ns)
            if materials is None:
                raise ValueError("3D Format Materials is missing")
            three_dim_format["materials"] = bool(materials.text.strip())
            log.debug(three_dim_format)
        return three_dim_format
