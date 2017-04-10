import xml.etree.ElementTree as ET

class EFG_XMLParser():

	def getRoot(self, filepath):
		tree = ET.parse(filepath)
		root = tree.getroot()

		return root
