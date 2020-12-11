#!.venv/bin/python3
import argparse
import datetime
import sys
from distutils.util import strtobool
from xml.etree import ElementTree as ET

from openpyxl import load_workbook

EFG_NAMESPACE = "http://www.europeanfilmgateway.eu/efg"
XSI_NAMESPACE = "http://www.w3.org/2001/XMLSchema-instance"
XSD_NAMESPACE = "http://www.w3.org/2001/XMLSchema"

ET.register_namespace("", EFG_NAMESPACE)

generated_on = str(datetime.datetime.now())
ALLOWED_ITEM_TYPES = ("Video",)

parser = argparse.ArgumentParser()
parser.add_argument("input", help="input excel file")
args = parser.parse_args()

input_filename = args.input
wb = None
try:
    wb = load_workbook(filename=input_filename, read_only=True, data_only=True)
except FileNotFoundError:
    sys.exit(f"ERROR: File '{input_filename}' not found")
# data_rows = []


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
    return not (my_string and my_string.strip())


# def lookup_field(row_idx, header):
#     for row in ws.iter_rows(min_row=1, max_col=25, max_row=1):
#         for c in [cell for cell in row if cell.value == header]:
#             val = ws.cell(row=row_idx, column=c.column).value
#             return val.strip() if val else None


def lookup_fields(row_idx, start_with, next_col=None):
    res = {}
    for header_row in ws.iter_rows(min_row=1, max_row=1):
        for c in [
            x
            for x in header_row
            if x.value is not None and x.value.startswith(start_with)
        ]:
            header_val = c.value.strip()
            # print(f"header: {header_val}")
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


def create_record():
    efg_entity = ET.Element(f"{{{EFG_NAMESPACE}}}efgEntity")
    av_creation = ET.SubElement(efg_entity, "avcreation")
    row_idx = row[0].row

    # identifier: attribute scheme= (1)
    identifier = ET.SubElement(av_creation, "identifier", scheme="CP_CATEGORY_ID")
    # identifier.text = lookup_field(row_idx, "identifier")
    identifier.text = ws.cell(row=row_idx, column=headers["identifier"]).value

    # recordSource (1-N)
    """
    <recordSource>
      <sourceID>20386</sourceID>
      <provider id="CCB" schemeID="Institution acronym">Cineteca di Bologna</provider>
    </recordSource>
    """
    record_source = ET.SubElement(av_creation, "recordSource")
    # source_id = lookup_field(row_idx, "sourceID")
    source_id = ws.cell(row=row_idx, column=headers["sourceID"]).value.strip()
    ET.SubElement(record_source, "sourceID").text = source_id
    # provider_id = lookup_field(row_idx, "provider_id")
    provider_id = ws.cell(row=row_idx, column=headers["provider_id"]).value
    ET.SubElement(
        record_source, "provider", schemeID="Institution acronym", id=provider_id
    ).text = ws.cell(row=row_idx, column=headers["provider"]).value

    # title (1-N)
    """
    <title lang="it">
      <text>Viaggio in Emilia Romagna</text>
      <relation>Original title</relation>
    </title>
    """
    # title
    titles = lookup_fields(row_idx, start_with="title_text", next_col="title_relation")
    for key, val in titles.items():
        title_el = ET.SubElement(av_creation, "title")
        title_el.set("lang", key)
        ET.SubElement(title_el, "text").text = val[0]
        if val[1]:
            ET.SubElement(title_el, "relation").text = val[1]

    # identifyingTitle (1)
    identifying_title = ET.SubElement(av_creation, "identifyingTitle")
    identifying_title.text = (
        ws.cell(row=row_idx, column=headers["identifyingTitle"]).value
        if headers.get("identifyingTitle")
        else list(titles.values())[0][0]
    )

    # countryOfReference (1-N)
    countries = ws.cell(row=row_idx, column=headers["countryOfReference"]).value
    if is_blank(countries):
        raise ValueError("Missing countryOfReference")
    for c in countries.split(sep=";"):
        country_of_reference = ET.SubElement(av_creation, "countryOfReference")
        country_of_reference.text = c.strip()

    # productionYear (1-N)
    years = ws.cell(row=row_idx, column=headers["productionYear"]).value
    if is_blank(years):
        raise ValueError("Missing productionYear")
    for y in years.split(sep=";"):
        production_year = ET.SubElement(av_creation, "productionYear")
        production_year.text = y.strip()

    # keywords (0-N)
    keywords = lookup_fields(row_idx, start_with="keywords")
    for key, val in keywords.items():
        # expected key is as follows: Subject_it, Place_it
        if len(key.split("_")) != 2:
            print(f"Warning: invalid keywords definition for <{key}>")
            continue
        k_type, lang = key.split("_")
        keywords_el = ET.SubElement(av_creation, "keywords")
        keywords_el.set("lang", lang)
        keywords_el.set("type", k_type)
        for term in val[0].split(";"):
            if is_blank(term):
                continue
            ET.SubElement(keywords_el, "term").text = term.strip()
    # description (0-N)
    descriptions = lookup_fields(row_idx, start_with="description")
    for key, val in descriptions.items():
        description_el = ET.SubElement(av_creation, "description")
        description_el.set("lang", key)
        description_el.text = val[0]

    # FIXME avManifestation (1-N)
    av_manifestation = ET.SubElement(av_creation, "avManifestation")
    # TODO identifier
    # TODO recordSource
    # TODO title
    # language (0-N)
    languages = ws.cell(row=row_idx, column=headers["language"]).value
    for lang in languages.split(sep=";"):
        if is_blank(lang):
            continue
        language = ET.SubElement(av_manifestation, "language")
        language.text = lang.strip()
    # duration (0-1)
    duration = ws.cell(row=row_idx, column=headers["duration"]).value
    if duration:
        ET.SubElement(av_manifestation, "duration").text = f"{duration}"
    # format (0-1)
    av_format = ET.SubElement(av_manifestation, "format")
    # gauge (0-1)
    if headers.get("gauge"):
        gauge = ws.cell(row=row_idx, column=headers["gauge"]).value
        if not is_blank(gauge):
            ET.SubElement(av_format, "gauge").text = gauge.strip()
    # aspectRatio (0-1)
    if headers.get("aspectRatio"):
        aspect_ratio = ws.cell(row=row_idx, column=headers["aspectRatio"]).value
        if not is_blank(aspect_ratio):
            ET.SubElement(av_format, "aspectRatio").text = aspect_ratio.strip()
    # colour (0-1)
    if headers.get("colour"):
        colour = ws.cell(row=row_idx, column=headers["colour"]).value
        if not is_blank(colour):
            ET.SubElement(av_format, "colour").text = colour.strip()
    # sound (0-1)
    if headers.get("hasSound"):
        has_sound = ws.cell(row=row_idx, column=headers["hasSound"]).value
        if has_sound is not None and not is_blank(f"{has_sound}"):
            has_sound = strtobool(f"{has_sound}")
            sound_el = ET.SubElement(av_format, "sound")
            sound_el.text = "With sound" if bool(has_sound) else "Without sound"
            sound_el.set("hasSound", "true" if bool(has_sound) else "false")
    # TODO rightHolder (0-N)
    # rightsStatus (0-N)
    rights_statuses = ws.cell(row=row_idx, column=headers["rightsStatus"]).value
    if rights_statuses is not None:
        for rs in rights_statuses.split(sep=";"):
            if is_blank(rs):
                continue
            ET.SubElement(av_manifestation, "rightsStatus").text = rs.strip()
    # thumbnail (1)
    thumbnail = ET.SubElement(av_manifestation, "thumbnail")
    thumbnail_url = ws.cell(row=row_idx, column=headers["thumbnail"]).value
    if is_blank(thumbnail_url):
        raise ValueError("Missing thumbnail")
    thumbnail.text = thumbnail_url.strip()
    # item/isShownAt (0-1)
    is_shown_at = ws.cell(row=row_idx, column=headers["isShownAt"]).value
    if not is_blank(is_shown_at):
        item = ET.SubElement(av_manifestation, "item")
        ET.SubElement(item, "isShownAt").text = is_shown_at.strip()

    # TODO relPerson (0-N)

    # TODO relCorporate (0-N)

    indent(efg_entity)

    # wrap it in an ElementTree instance, and save as XML
    tree = ET.ElementTree(efg_entity)

    tree.write(
        f"test_{source_id}.xml", xml_declaration=True, encoding="utf-8", method="xml"
    )


# iterate over worksheets
for ws in [a for a in wb.worksheets if a.title in ALLOWED_ITEM_TYPES]:
    print(f"Worksheet {ws.title}")
    headers = {}
    for row in ws.iter_rows(min_row=1, max_row=1):
        for cell in row:
            headers[cell.value] = cell.column
    # print(headers)
    counter = 0
    for row in ws.iter_rows(2, ws.max_row + 1):
        if row[0].value is not None:
            counter += 1
            create_record()
            break
            # data_rows.append([cell.value for cell in row])
        else:
            continue
    print(f"Total {ws.title} items: {counter}")

# print(f"Total items: {len(data_rows)}")
