
from utilities.logs import get_logger
from neomodel import db

log = get_logger(__name__)


class CreationRepository():
    """ """

    def __init__(self, graph):
        self.graph = graph

    @db.transaction
    def create_av_entity(self, properties, item, relationships):

        # check if a creation already exists and delete it
        existing_creation = item.creation.single()
        if existing_creation is not None:
            log.debug("Creation already exists for current Item")
            creation_id = existing_creation.uuid
            self.delete_av_entity(existing_creation)
            log.info(
                "Existing creation [UUID:{0}] deleted".format(creation_id))
            # use the same uuid for the new replacing creation
            properties['uuid'] = creation_id

        av_entity = self.graph.AVEntity(**properties).save()
        # connect to item
        item.creation.connect(av_entity)

        # add relatioships
        for r in relationships.keys():
            if r == 'record_sources':
                # connect to record sources
                for rc in relationships[r]:
                    rc_node = self.create_record_source(rc)
                    av_entity.record_sources.connect(rc_node)
            elif r == 'titles':
                # connect to titles
                for title in relationships[r]:
                    title_node = self.create_title(title)
                    av_entity.titles.connect(title_node)
            elif r == 'keywords':
                # connect to keywords
                for keyword in relationships[r]:
                    keyword_node = self.create_keyword(keyword)
                    av_entity.keywords.connect(keyword_node)
            elif r == 'descriptions':
                # connect to descriptions
                for description in relationships[r]:
                    description_node = self.create_description(description)
                    av_entity.descriptions.connect(description_node)
            elif r == 'languages':
                # connect to languages
                for lang_usage in relationships[r]:
                    lang = self.graph.Language.nodes.get_or_none(
                        code=lang_usage[0])
                    if lang is None:
                        lang = self.graph.Language(code=lang_usage[0]).save()
                    av_entity.languages.connect(lang, {'usage': lang_usage[1]})
            elif r == 'coverages':
                for coverage in relationships[r]:
                    # connect to coverages
                    coverage_node = coverage.save()
                    av_entity.coverages.connect(coverage_node)
            elif r == 'production_countries':
                for country_reference in relationships[r]:
                    country = self.graph.Country.nodes.get_or_none(
                        code=country_reference[0])
                    if country is None:
                        country = self.graph.Country(
                            code=country_reference[0]).save()
                    av_entity.production_countries.connect(
                        country, {'reference': country_reference[1]})

        return av_entity

    def delete_av_entity(self, node):
        for rc in node.record_sources.all():
            rc.delete()
        for title in node.titles.all():
            self.delete_title(title)
        for description in node.descriptions.all():
            self.delete_description(description)
        for keyword in node.keywords.all():
            self.delete_keyword(keyword)
        for coverage in node.coverages:
            coverage.delete()
        node.delete()

    def create_record_source(self, record_source):
        record_source.save()
        return record_source

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
