# -*- coding: utf-8 -*-

"""
sudo pip3 install click pyoai
"""

import click
import json
import os
import codecs
# import urllib
import re
import html
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from oaipmh.error import NoRecordsMatchError
from lxml import etree
import time
from datetime import datetime
from utilities.logs import get_logger

log = get_logger(__name__)


# for s in client.listSets()
#     print(s)

# for f in client.listMetadataFormats():
#     print(f)

def tag(tag):
    tag_prefix = '{http://www.europeanfilmgateway.eu/efg}'
    return "%s%s" % (tag_prefix, tag)


def parse_date(date_string):

        try:
            fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
            d = datetime.strptime(date_string, fmt)
            log.info(
                "time data '%s' matches format '%s'", date_string, fmt)
            return d
        except ValueError as e:
            log.warning(e)
            try:
                fmt = "%Y-%m-%d"
                d = datetime.strptime(date_string, fmt)
                log.info(
                    "time data '%s' matches format '%s'", date_string, fmt)
                return d
            except ValueError as e:
                log.error(e)

        return None


@click.command()
@click.option('--metadata_set', prompt='Name of set to be retrieved',
              help='Examples: fdc, ofm, mnc')
@click.option('--dest_folder', prompt='Path of destination folder',
              help='Path of destination folder')
@click.option('--log_file', prompt='Name of log file',
              help='Name of log file')
@click.option('--content-type',
              help='Type of content, e.g. video')
@click.option('--from', 'from_date',
              help='Downloading content starting from this date')
@click.option('--until', 'until_date',
              help='Downloading content only until this date')
def harvest(metadata_set, dest_folder, log_file, content_type,
            from_date, until_date):

    #############################
    # ### FILESYSTEM CHECKS ### #
    #############################
    try:
        if not os.path.isdir(dest_folder):
            os.makedirs(dest_folder)
        # Verify write permission inside the folder:
    except BaseException as e:
        log.error(str(e))
        log.exit("Unable to create destination folder: %s" % dest_folder)

    try:
        test_path = os.path.join(dest_folder, '__test_permissions__')
        os.makedirs(test_path)
        os.rmdir(test_path)
    except BaseException as e:
        log.error(str(e))
        log.exit("Unable to use destination folder: %s" % dest_folder)

    try:
        log_handle = open(log_file, 'a+')
        log_handle.close()
    except BaseException as e:
        log.error(str(e))
        log.exit("Unable to create log_file: %s" % log_file)

    #################################
    # ### OAI-PMH CONFIGURATION ### #
    #################################
    URL = 'https://node0-d-efg.d4science.org/efg/mvc/oai/oai.do'
    metadata_prefix = 'efg'

    ###################################
    # ### OPEN OAI-PMH CONNECTION ### #
    ###################################
    registry = MetadataRegistry()
    registry.registerReader(metadata_prefix, oai_dc_reader)
    client = Client(URL, registry)

    ####################################
    # ### CHECK IF THIS SET EXISTS ### #
    ####################################
    set_found = False
    for s in client.listSets():
        if metadata_set == s[0]:
            set_found = True

    if not set_found:
        log.exit("Unable to find this set: %s" % metadata_set)

    #############################
    # ### RETRIEVE METADATA ### #
    #############################

    if from_date is not None:
        from_date = parse_date(from_date)
        if from_date is None:
            log.exit("Unable to convert from date")

    if until_date is not None:
        until_date = parse_date(until_date)
        if until_date is None:
            log.exit("Unable to convert until date")

    report_data = {
        'downloaded': 0,
        'filtered': 0,
        'saved': 0,
        'saved_files': [],
        'missing_sourceid': [],
        'wrong_content_type': []
    }
    timestamp = int(1000 * time.time())
    log.info("Retrieving records for %s..." % metadata_set)
    try:
        records = client.listRecords(
            metadataPrefix=metadata_prefix,
            set=metadata_set,
            from_=from_date,
            until=until_date)
    except NoRecordsMatchError as e:
        log.exit(e)

    log.info("Records retrieved, extracting...")
    try:
        for record in records:
            element = record[1].element()
            # Obtained eTree is based on namespaced XML
            # Read: 19.7.1.6. Parsing XML with Namespaces
            # https://docs.python.org/2/library/xml.etree.elementtree.html

            # find(match)
            # Finds the first subelement matching match.
            #   match may be a tag name or path.
            #   Returns an element instance or None.

            # findall(match)
            # Finds all matching subelements, by tag name or path.
            #   Returns a list containing all matching elements
            #   in document order.

            report_data['downloaded'] += 1

            if report_data['downloaded'] % 100 == 0:
                print('.', end='', flush=True)

                if report_data['downloaded'] % 5000 == 0:
                    print(
                        ' %s downloaded - %s saved' % (
                            report_data['downloaded'],
                            report_data['saved']
                        ), flush=True)

            efgEntity = element.find(tag("efgEntity"))
            if efgEntity is None:
                # log.warning("efgEntity not found, skipping record")
                continue
            avcreation = efgEntity.find(tag("avcreation"))
            nonavcreation = efgEntity.find(tag("nonavcreation"))

            if avcreation is not None:
                manifestation = avcreation.find(tag("avManifestation"))
                # recordSource = avcreation.find(tag("recordSource"))
                keywords = avcreation.findall(tag("keywords"))
                title_el = avcreation.find(tag("identifyingTitle"))
                title = (title_el.text
                         if title_el is not None
                         else "Unknown title")
            elif nonavcreation is not None:
                manifestation = nonavcreation.find(tag("nonAVManifestation"))
                # recordSource = nonavcreation.find(tag("recordSource"))
                keywords = nonavcreation.findall(tag("keywords"))
                title_el = nonavcreation.find(tag("title"))
                title = (title_el.find(tag("text")).text
                         if title_el is not None
                         else "Unknown title")
            else:
                title = "Unknown title"
                # log.warning("(non)avcreation not found, skipping record")
                continue

            filter_keyword = "IMediaCities"
            is_good = False
            for keyword in keywords:
                term = keyword.find(tag("term"))
                if term.text == filter_keyword:
                    is_good = True
                    break

            if not is_good:
                continue

            report_data['filtered'] += 1

            if manifestation is None:
                report_data['missing_sourceid'].append(title)
                # log.warning("avManifestation not found, skipping record")
                continue

            if content_type is not None:
                content_type = content_type.lower()

                item = manifestation.find(tag("item"))
                if item is None:
                    # missing <item> => type cannot be found
                    report_data['wrong_content_type'].append(title)
                    continue

                item_type = item.find(tag("type"))
                if item_type is None:
                    # missing <type>
                    report_data['wrong_content_type'].append(title)
                    continue

                if item_type.text.lower() != content_type:
                    # wrong type
                    report_data['wrong_content_type'].append(title)
                    continue

            recordSource = manifestation.find(tag("recordSource"))
            if recordSource is None:
                report_data['missing_sourceid'].append(title)
                # log.warning("recordSource not found, skipping record")
                continue

            sourceID = recordSource.find(tag("sourceID"))
            if sourceID is None:
                report_data['missing_sourceid'].append(title)
                # log.warning("sourceID not found, skipping record")
                continue

            content = etree.tostring(efgEntity, pretty_print=True)

            # id_text = urllib.parse.quote_plus(sourceID.text.strip())
            # replace non alpha-numeric characters with a dash
            id_text = re.sub(r'[\W_]+', '-', sourceID.text.strip())
            # fine cinzia

            filename = "%s_%s_%s.xml" % (
                metadata_set,
                id_text,
                timestamp
            )
            filepath = os.path.join(dest_folder, filename)
            # with open(filepath, 'wb') as f:
            with codecs.open(filepath, 'wb', "utf-8") as f:
                f.write(html.unescape(content.decode('utf-8')))

            report_data['saved'] += 1
            report_data['saved_files'].append(filename)
    except NoRecordsMatchError as e:
        log.warning("No more records after filtering?")
        log.warning(e)

        # ###################
        # Write report file
        # ###################

        # the procedure writes a report file containing the results
        #     of the harvesting:
        # the list of records that do not contain the record ID
        #     (by writing the content of the element title)

    with open(log_file, 'w+') as f:
        json.dump(report_data, f)

    f.close()

    # Just to close previous dot line
    print("")

    log.info("""

%s records from set [%s] downloaded
open log file [%s] for details
""" % (report_data['saved'], metadata_set, log_file)
    )

    # log.info("Report data for set %s" % (metadata_set))
    # log.info("Downloaded %d records" % (report_data['downloaded']))
    # log.info("Filtered %d records" % (report_data['filtered']))
    # log.info("Saved %d records" % (report_data['saved']))

    # for s in report_data['saved_files']:
    #     log.info(s)

    # for s in report_data['missing_sourceid']:
    #     log.warning(s)


if __name__ == '__main__':
    harvest()
