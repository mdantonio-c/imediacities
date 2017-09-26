# -*- coding: utf-8 -*-

"""
sudo pip3 install pyoai
"""

import click
import json
import os
import urllib
from oaipmh.client import Client
from oaipmh.metadata import MetadataRegistry, oai_dc_reader
from lxml import etree
import time
from utilities.logs import get_logger

log = get_logger(__name__)


# for s in client.listSets()
#     print(s)

# for f in client.listMetadataFormats():
#     print(f)

def tag(tag):
    tag_prefix = '{http://www.europeanfilmgateway.eu/efg}'
    return "%s%s" % (tag_prefix, tag)


@click.command()
@click.option('--metadata_set', prompt='Name of set to be retrieved',
              help='Examples: fdc, ofm, mnc')
@click.option('--dest_folder', prompt='Path of destination folder',
              help='Path of destination folder')
@click.option('--log_file', prompt='Name of log file',
              help='Name of log file')
def harvest(metadata_set, dest_folder, log_file):

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
    metadata_prefix='efg'

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
    report_data = {
        'downloaded': 0,
        'filtered': 0,
        'saved': 0,
        'saved_files': [],
        'missing_sourceid': []
    }
    timestamp = int(1000 * time.time())
    for record in client.listRecords(
            metadataPrefix=metadata_prefix,
            set=metadata_set):
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

        efgEntity = element.find(tag("efgEntity"))
        if efgEntity is None:
            # log.warning("efgEntity not found, skipping record")
            continue
        avcreation = efgEntity.find(tag("avcreation"))
        nonavcreation = efgEntity.find(tag("nonavcreation"))

        if avcreation is not None:
            avManifestation = avcreation.find(tag("avManifestation"))
            keywords = avcreation.findall(tag("keywords"))
            title = avcreation.find(tag("title")).find(tag("text")).text
        elif nonavcreation is not None:
            avManifestation = nonavcreation.find(tag("avManifestation"))
            keywords = nonavcreation.findall(tag("keywords"))
            title = nonavcreation.find(tag("title")).find(tag("text")).text
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

        if avManifestation is None:
            report_data['missing_sourceid'].append(title)
            # log.warning("avManifestation not found, skipping record")
            continue

        recordSource = avManifestation.find(tag("recordSource"))
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

        id_text = urllib.parse.quote_plus(sourceID.text)
        filename = "%s_%s_%s.xml" % (
            metadata_set,
            id_text,
            timestamp
        )
        with open(os.path.join(dest_folder, filename), 'wb') as f:
            f.write(content)

        report_data['saved'] += 1
        report_data['saved_files'].append(filename)

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
