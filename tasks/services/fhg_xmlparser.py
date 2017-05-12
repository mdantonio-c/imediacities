import os
import xml.etree.ElementTree as ET
# from xml.dom import minidom
from imc.models.neo4j import (
    Shot
)
from rapydo.utils.logs import get_logger

log = get_logger(__name__)


class FHG_XMLParser():

    def get_root(self, filepath):
        tree = ET.parse(filepath)
        root = tree.getroot()

        return root

    def get_shot_module(self, filepath):
        root = ET.parse(filepath)
        nodes = root.findall("./module[@name='Shot']")
        if len(nodes) <= 0:
            return None
        return nodes[0]

    def get_shots(self, filepath):
        shot_module_node = self.get_shot_module(filepath)
        if shot_module_node is None:
            return None
        shots = []
        start_idx = 1
        for frame in shot_module_node.iter('frame'):
            end_idx = frame.get('idx')
            shot = Shot(start_frame_idx=start_idx, end_frame_idx=end_idx)
            frame_filename = 'tvs_s_' + str(end_idx).zfill(5) + '.jpg'
            shot.frame_uri = os.path.join(filepath, frame_filename)
            shots.append(shot)
            start_idx = int(end_idx) + 1
        return shots

    def get_key_frame_module(self, filepath):
        root = ET.parse(filepath)
        nodes = root.findall("./module[@name='KeyFrame']")
        if len(nodes) <= 0:
            return None
        return nodes[0]
