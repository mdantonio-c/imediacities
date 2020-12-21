#!.venv/bin/python3
import argparse
import copy
import datetime
import os
import sys
from distutils.util import strtobool
from xml.etree import ElementTree as ET

from openpyxl import load_workbook
from openpyxl.utils.exceptions import InvalidFileException

EFG_NAMESPACE = "http://www.europeanfilmgateway.eu/efg"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"

ET.register_namespace("", EFG_NAMESPACE)

generated_on = str(datetime.datetime.now())
ALLOWED_ITEM_TYPES = ("Image", "Video")
COMMON_MANDATORY_COLS = [
    "identifier",
    "sourceID",
    "provider",
    "provider_id",
    "thumbnail",
]

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input excel file")
parser.add_argument(
    "-t", "--target-directory", help="put all generated files into TARGET DIRECTORY"
)
parser.add_argument("-p", "--prefix", help="set a prefix to output filename")
args = parser.parse_args()
input_filename = args.input
# check target directory
target_dir = args.target_directory
if target_dir and not os.path.isdir(target_dir):
    exit(f"ERROR - Target director '{target_dir}' does NOT exist")

wb = None
try:
    wb = load_workbook(filename=input_filename, read_only=True, data_only=True)
except (InvalidFileException, FileNotFoundError) as e:
    sys.exit(f"ERROR - {e}")


def indent(elem, level=0):
    i = "\n" + level * "  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def is_blank(my_string):
    return not (my_string and str(my_string).strip())


def lookup_fields(row_idx, start_with, next_col=None):
    res = {}
    for header_row in ws.iter_rows(min_row=1, max_row=1):
        for c in [
            x
            for x in header_row
            if x.value is not None and x.value.startswith(start_with)
        ]:
            header_val = c.value.strip()
            key = header_val[len(start_with) + 1 :]
            val = ws.cell(row=row_idx, column=c.column).value
            next_val = None
            if next_col and ws.cell(row=c.row, column=c.column + 1).value == next_col:
                next_val = ws.cell(row=row_idx, column=c.column + 1).value
            res[key] = (
                val.strip() if val else None,
                next_val.strip() if next_val else None,
            )
    return res


def parse_related_entities(row_idx, el_name, parent):
    agents = ws.cell(row=row_idx, column=headers[el_name]).value
    if agents is None:
        return
    for agent in agents.split(sep=";"):
        if is_blank(agent):
            continue
        agent = agent.strip()
        rel_agent = ET.SubElement(parent, el_name)
        agent_id, agent_name, agent_type = None, None, None
        try:
            tokens = agent.strip().split(":", 2)
            agent_id = tokens[0]
            agent_name = tokens[1]
            agent_type = tokens[2]
        except IndexError:
            pass
        ET.SubElement(rel_agent, "identifier").text = agent_id.strip()
        if not agent_name:
            print(
                f"WARNING - Record[{row_idx}]. Expected name in form of 'identifier:name:?type'. Invalid value for '{agent}'"
            )
            continue
        ET.SubElement(rel_agent, "name").text = agent_name.strip()
        if agent_type:
            ET.SubElement(rel_agent, "type").text = agent_type.strip()


def create_record():
    efg_entity = ET.Element(f"{{{EFG_NAMESPACE}}}efgEntity")
    c_tag = "avcreation" if ws.title == "Video" else "nonavcreation"
    creation = ET.SubElement(efg_entity, c_tag)
    row_idx = row[0].row

    # identifier: attribute scheme= (1)
    identifier = ET.SubElement(creation, "identifier", scheme="CP_CATEGORY_ID")
    identifier.text = ws.cell(row=row_idx, column=headers["identifier"]).value

    # recordSource (1-N)
    record_source = ET.SubElement(creation, "recordSource")
    # source_id = lookup_field(row_idx, "sourceID")
    source_id = ws.cell(row=row_idx, column=headers["sourceID"]).value.strip()
    ET.SubElement(record_source, "sourceID").text = source_id
    # provider_id = lookup_field(row_idx, "provider_id")
    provider_id = ws.cell(row=row_idx, column=headers["provider_id"]).value
    ET.SubElement(
        record_source, "provider", schemeID="Institution acronym", id=provider_id
    ).text = ws.cell(row=row_idx, column=headers["provider"]).value

    # title (1-N)
    titles = lookup_fields(row_idx, start_with="title_text", next_col="title_relation")
    for key, val in titles.items():
        title_el = ET.SubElement(creation, "title")
        title_el.set("lang", key)
        ET.SubElement(title_el, "text").text = val[0]
        if val[1]:
            ET.SubElement(title_el, "relation").text = val[1]

    # identifyingTitle (1)
    identifying_title = ET.SubElement(creation, "identifyingTitle")
    identifying_title.text = (
        ws.cell(row=row_idx, column=headers["identifyingTitle"]).value
        if headers.get("identifyingTitle")
        else list(titles.values())[0][0]
    )

    if ws.title == "Video":
        # countryOfReference (1-N)
        countries = ws.cell(row=row_idx, column=headers["countryOfReference"]).value
        if is_blank(countries):
            raise ValueError("Missing countryOfReference")
        for c in countries.split(sep=";"):
            country_of_reference = ET.SubElement(creation, "countryOfReference")
            country_of_reference.text = c.strip()

        # productionYear (1-N)
        years = ws.cell(row=row_idx, column=headers["productionYear"]).value
        if is_blank(years):
            raise ValueError("Missing productionYear")
        for y in str(years).split(sep=";"):
            production_year = ET.SubElement(creation, "productionYear")
            production_year.text = y.strip()
    else:
        # dateCreated
        date_created = ws.cell(row=row_idx, column=headers["dateCreated"]).value
        if not date_created or (
            isinstance(date_created, str) and is_blank(date_created)
        ):
            raise ValueError("Missing dateCreated")
        ET.SubElement(creation, "date_created").text = (
            date_created.strip() if isinstance(date_created, str) else date_created
        )

    # keywords (0-N)
    keywords = lookup_fields(row_idx, start_with="keywords")
    for key, val in keywords.items():
        # expected key is as follows: Subject_it, Place_it
        if len(key.split("_")) != 2:
            # ignore invalid keywords definitions
            continue
        k_type, lang = key.split("_")
        keywords_el = ET.SubElement(creation, "keywords")
        keywords_el.set("lang", lang)
        keywords_el.set("type", k_type)
        for term in val[0].split(";"):
            if is_blank(term):
                continue
            ET.SubElement(keywords_el, "term").text = term.strip()

    # description (0-N)
    descriptions = lookup_fields(row_idx, start_with="description")
    for key, val in descriptions.items():
        description_el = ET.SubElement(creation, "description")
        description_el.set("lang", key)
        description_el.text = val[0]

    # avManifestation (1-N)
    m_tag = "avManifestation" if ws.title == "Video" else "nonAVManifestation"
    manifestation = ET.SubElement(creation, m_tag)
    # identifier
    manifestation.append(copy.deepcopy(identifier))
    # recordSource
    manifestation.append(copy.deepcopy(record_source))
    # title
    title_node = creation.find("./title[1]")
    if title_node:
        manifestation.append(copy.deepcopy(title_node))
    # language (0-N)
    if "language" in headers:
        languages = ws.cell(row=row_idx, column=headers["language"]).value
        if languages:
            for lang in languages.split(sep=";"):
                if is_blank(lang):
                    continue
                language = ET.SubElement(manifestation, "language")
                language.text = lang.strip()
    if m_tag == "avManifestation":
        # duration (0-1)
        if "duration" in headers:
            duration = ws.cell(row=row_idx, column=headers["duration"]).value
            if duration:
                ET.SubElement(manifestation, "duration").text = f"{duration}"
        # format (0-1)
        av_format = ET.SubElement(manifestation, "format")
        # gauge (0-1)
        if "gauge" in headers:
            gauge = ws.cell(row=row_idx, column=headers["gauge"]).value
            if not is_blank(gauge):
                ET.SubElement(av_format, "gauge").text = gauge.strip()
        # aspectRatio (0-1)
        if "aspectRatio" in headers:
            aspect_ratio = ws.cell(row=row_idx, column=headers["aspectRatio"]).value
            if not is_blank(aspect_ratio):
                ET.SubElement(av_format, "aspectRatio").text = aspect_ratio.strip()
        # colour (0-1)
        if "colour" in headers:
            colour = ws.cell(row=row_idx, column=headers["colour"]).value
            if not is_blank(colour):
                ET.SubElement(av_format, "colour").text = colour.strip()
        # sound (0-1)
        if "hasSound" in headers:
            has_sound = ws.cell(row=row_idx, column=headers["hasSound"]).value
            if has_sound is not None and not is_blank(f"{has_sound}"):
                has_sound = strtobool(f"{has_sound}")
                sound_el = ET.SubElement(av_format, "sound")
                sound_el.text = "With sound" if bool(has_sound) else "Without sound"
                sound_el.set("hasSound", "true" if bool(has_sound) else "false")
    if m_tag == "nonAVManifestation":
        ET.SubElement(manifestation, "type").text = "image"
        specific_type = ws.cell(row=row_idx, column=headers["specificType"]).value
        if is_blank(specific_type):
            raise ValueError("Missing SpecificType")
        ET.SubElement(manifestation, "specificType").text = specific_type.strip()
        if "physicalFormat" in headers and not is_blank(
            physical_format := ws.cell(
                row=row_idx, column=headers["physicalFormat"]
            ).value
        ):
            ET.SubElement(
                manifestation, "physicalFormat"
            ).text = physical_format.strip()
        if "colour" in headers and not is_blank(
            colour := ws.cell(row=row_idx, column=headers["colour"]).value
        ):
            ET.SubElement(manifestation, "colour").text = colour.strip()
    # rightsHolder (0-N)
    if headers.get("rightsHolder"):
        rights_holders = ws.cell(row=row_idx, column=headers["rightsHolder"]).value
        for rh in rights_holders.split(sep=";"):
            if is_blank(rh):
                continue
            rights_holder = ET.SubElement(manifestation, "rightsHolder")
            rights_holder.text = rh.strip()
    # rightsStatus (0-N)
    rights_statuses = ws.cell(row=row_idx, column=headers["rightsStatus"]).value
    if rights_statuses is not None:
        for rs in rights_statuses.split(sep=";"):
            if is_blank(rs):
                continue
            ET.SubElement(manifestation, "rightsStatus").text = rs.strip()
    # thumbnail (1)
    thumbnail = ET.SubElement(manifestation, "thumbnail")
    thumbnail_url = ws.cell(row=row_idx, column=headers["thumbnail"]).value
    if is_blank(thumbnail_url):
        raise ValueError("Missing thumbnail")
    thumbnail.text = thumbnail_url.strip()
    if m_tag == "avManifestation" and "isShownAt" in headers:
        # item/isShownAt (0-1)
        is_shown_at = ws.cell(row=row_idx, column=headers["isShownAt"]).value
        if not is_blank(is_shown_at):
            item = ET.SubElement(manifestation, "item")
            ET.SubElement(item, "isShownAt").text = is_shown_at.strip()
        # item/type (0-1)
        ET.SubElement(manifestation, "type").text = "video"
    # relPerson (0-N)
    if headers.get("relPerson"):
        parse_related_entities(row_idx, "relPerson", creation)
    # relCorporate (0-N)
    if headers.get("relCorporate"):
        parse_related_entities(row_idx, "relCorporate", creation)
    # relCollection (0-N)
    if headers.get("relCollection"):
        parse_related_entities(row_idx, "relCollection", creation)

    indent(efg_entity)

    # wrap it in an ElementTree instance, and save as XML
    tree = ET.ElementTree(efg_entity)
    global target_dir
    if target_dir is None:
        target_dir = ""
    prefix = ""
    if args.prefix:
        prefix = f"{args.prefix}_"
    tree.write(
        os.path.join(target_dir, f"{prefix}{source_id}.xml"),
        xml_declaration=True,
        encoding="utf-8",
        method="xml",
    )


def check_mandatory_columns():
    for col in COMMON_MANDATORY_COLS:
        if col not in headers:
            raise ValueError(f"Missing mandatory column <{col}>")
    if not [n for n in headers.keys() if n and n.startswith("title_text_")]:
        raise ValueError("Missing mandatory column <title_text>")
    if ws.title == "Video":
        for col in ["countryOfReference", "productionYear"]:
            if col not in headers:
                raise ValueError(f"Missing mandatory column <{col}>")
    elif ws.title == "Image":
        for col in ["dateCreated", "specificType"]:
            if col not in headers:
                raise ValueError(f"Missing mandatory column <{col}>")


# iterate over worksheets
for ws in [a for a in wb.worksheets if a.title in ALLOWED_ITEM_TYPES]:
    print(f"Worksheet {ws.title}")
    headers = {}
    for row in ws.iter_rows(min_row=1, max_row=1):
        for cell in row:
            headers[cell.value] = cell.column
    try:
        check_mandatory_columns()
    except ValueError as err:
        print(f"ERROR - Worksheet {ws.title} cannot be parsed. Reason: {err}")
        continue
    counter = 0
    err_counter = 0
    for row in ws.iter_rows(2, ws.max_row + 1):
        if row[0].value is not None:
            counter += 1
            try:
                create_record()
            except ValueError as err:
                err_counter += 1
                print(f"ERROR - Record[{row[0].row}] cannot be parsed: {err}")

    print(
        f"Total {ws.title} items: {counter} [SUCCESS:{counter-err_counter}, FAILURE:{err_counter}]"
    )
