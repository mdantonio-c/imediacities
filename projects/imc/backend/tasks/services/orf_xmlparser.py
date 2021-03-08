from typing import Any, Dict, List
from xml.etree import ElementTree as ET

from restapi.utilities.logs import log

__author__ = "Silvano Imboden(s.imboden@cineca.it)"


class ORF_XMLParser:
    def parse(self, xmlfile):
        xml_tree = ET.ElementTree(file=xmlfile)
        xml_root = xml_tree.getroot()
        xml_labels = xml_root.find("labels")
        labels = {}
        for label in xml_labels:  # type: ignore
            lid = int(label.get("uid"))  # type: ignore
            name = label.get("name")
            labels[int(lid)] = name

        frames: Dict[int, List[Any]] = {}
        xml_frames = xml_root.find("frames")  # type: ignore
        for n in xml_frames:
            timestamp = int(n.get("timestamp"))
            frames[timestamp] = []

            xml_mappings = n.find("mappings")
            mappings = {}  # type: ignore
            for m in xml_mappings:
                oref = m.attrib["object_ref"]
                lref = int(m.attrib["label_ref"])
                conf = float(m.attrib["confidence"])
                # always take the object with the highest confidence
                if (oref not in mappings) or (mappings[oref][1] < conf):
                    mappings[oref] = (labels[lref], conf)

            xml_objects = n.find("objects")
            for o in xml_objects.findall("object"):

                xml_region = o.find("region")
                oid = o.attrib["uid"]
                rect = [None, None, None, None]
                for p in xml_region.findall("point"):
                    x = float(p.attrib["posX"])
                    y = float(p.attrib["posY"])
                    i = int(p.attrib["orderIdx"])
                    rect[i] = (x, y)
                # regions are not always present (e.g. for buildings)
                lab, conf = mappings[oid]
                frames[timestamp].append((oid, lab, conf, rect))

        log.debug("done reading orf")
        return frames
