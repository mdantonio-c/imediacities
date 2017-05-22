
from rapydo.utils.logs import get_logger
from neomodel import db

log = get_logger(__name__)


class CreationRepository():
    """ """

    def __init__(self, graph):
        self.graph = graph

    @db.transaction
    def create_av_entity(
            self, properties, item, titles, keywords, descriptions):

        # check if a creation already exists and delete it
        existing_creation = item.creation.single()
        if existing_creation is not None:
            log.debug("Creation already exists for current Item")
            creation_id = existing_creation.uuid
            self.delete_av_entity(existing_creation)
            log.info(
                "Existing creation [UUID:%s] deleted" % creation_id)
            # use the same uuid for the new replacing creation
            properties['uuid'] = creation_id

        # extend properties with something more
        # properties["other_info"] = "XXX"

        av_entity_node = self.graph.AVEntity(**properties).save()
        # connect to item
        item.creation.connect(av_entity_node)
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

    def delete_av_entity(self, node):
        for title in node.titles.all():
            self.delete_title(title)
        for description in node.descriptions.all():
            self.delete_description(description)
        for keyword in node.keywords.all():
            self.delete_keyword(keyword)
        node.delete()

    def create_title(self, title):
        if title.relationship is None:
            title.relationship = '00'
        # return self.graph.Title(**title).save()
        title.save()
        return title

    def delete_title(self, node):
        node.delete()

    def create_keyword(self, keyword):
        keyword.save()
        return keyword

    def delete_keyword(self, node):
        node.delete()

    def create_description(self, description):
        description.save()
        return description

    def delete_description(self, node):
        node.delete()

    def search_item_by_term(self, term, item_type):
        """
        Search all types of items and see whether some attributes matches the
        value provided by the user.
        """
        log.debug("Searching for Items with term = " % term)
        pass
