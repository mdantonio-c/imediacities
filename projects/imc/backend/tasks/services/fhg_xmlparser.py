import os
import xml.etree.ElementTree as ET

# from xml.dom import minidom
from imc.models.neo4j import Shot
# from restapi.utilities.logs import log


class FHG_XMLParser:
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
        tvs_dirname = os.path.dirname(filepath)
        for frame in shot_module_node.iter('frame'):
            start_idx = frame.get('idx')
            shot = Shot(start_frame_idx=start_idx)
            frame_filename = 'tvs_s_' + str(start_idx).zfill(5) + '.jpg'
            shot.frame_uri = os.path.join(tvs_dirname, frame_filename)
            shot.thumbnail_uri = os.path.join(tvs_dirname, 'thumbs/' + frame_filename)
            shots.append(shot)
        return shots

    def get_key_frame_module(self, filepath):
        root = ET.parse(filepath)
        nodes = root.findall("./module[@name='KeyFrame']")
        if len(nodes) <= 0:
            return None
        return nodes[0]
