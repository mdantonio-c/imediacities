
from commons.logs import get_logger

log = get_logger(__name__)


class CreationRepository():
    """ """

    def __init__(self, graph):
        self.graph = graph

    def create_av_entity(
            self, properties, item, titles, keywords, descriptions):

        # extend properties with something more
        # properties["other_info"] = "XXX"

        av_entity_node = self.graph.AVEntity(**properties).save()
        # connect to item
        av_entity_node.item.connect(item)
        # connect to tiles
        for title in titles:
            title_node = self.create_title(title)
            av_entity_node.titles.connect(title_node)
        # connect to keywords
        for keyword in keywords:
            keyword_node = self.create_keyword(keyword)
            av_entity_node.keywords.connect(keyword_node)
        # connect to descriptions
        for description in descriptions:
            description_node = self.create_description(description)
            av_entity_node.descriptions.connect(description_node)

        return av_entity_node

    def create_title(self, properties):
        # FIXME
        properties['relationship'] = '00'
        return self.graph.Title(**properties).save()

    def create_keyword(self, properties):
        return self.graph.Keyword(**properties).save()

    def create_description(self, properties):
        return self.graph.Description(**properties).save()
