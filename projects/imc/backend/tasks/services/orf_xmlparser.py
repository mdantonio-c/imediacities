# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET

from utilities.logs import get_logger

logger = get_logger(__name__)

__author__ = "Silvano Imboden(s.imboden@cineca.it)"


class ORF_XMLParser():

    def parse(self, xmlfile):
        xml_tree = ET.ElementTree(file=xmlfile)
        xml_root = xml_tree.getroot()
        xml_labels = xml_root.find('labels')
        labels = {}
        for label in xml_labels:
            lid  = int(label.get('uid'))
            name = label.get('name')
            # logger.debug("label id: {0}, name: {1}".format(lid, name))
            labels[int(lid)] = name

        frames = {}
        xml_frames = xml_root.find('frames')
        for n in xml_frames:
            timestamp = int(n.get('timestamp'))
            frames[timestamp] = []

            xml_mappings = n.find('mappings')
            mappings = {}
            for m in xml_mappings:
                oref  = m.attrib['object_ref']
                lref  = int(m.attrib['label_ref'])
                conf  = float(m.attrib['confidence'])
                # always take the object with the highest confidence
                if (oref not in mappings) or (mappings[oref][1] < conf):
                    mappings[oref] = (labels[lref], conf)

            xml_objects  = n.find('objects')
            for o in xml_objects.findall('object'):

                xml_region = o.find('region')
                oid = o.attrib['uid']
                rect = [None, None, None, None]
                for p in xml_region.findall('point'):
                    x = float(p.attrib['posX'])
                    y = float(p.attrib['posY'])
                    i = int(p.attrib['orderIdx'])
                    rect[i] = (x, y)
                # regions are not always present (e.g. for buildings)
                lab, conf = mappings[oid]
                frames[timestamp].append((oid, lab, conf, rect))

        logger.debug('done reading orf')
        return frames
