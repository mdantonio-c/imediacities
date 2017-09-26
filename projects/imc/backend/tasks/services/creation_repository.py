
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
                for item in relationships[r]:
                    record_source = item[0].save()
                    av_entity.record_sources.connect(record_source)
                    # look for existing content provider
                    provider = self.find_provider_by_identifier(
                        item[1].identifier, item[1].scheme)
                    if provider is None:
                        provider = item[1].save()
                    record_source.provider.connect(provider)
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
            elif r == 'video_format':
                video_format = relationships[r].save()
                av_entity.video_format.connect(video_format)
            elif r == 'agents':
                for agent_activities in relationships[r]:
                    # look for existing agents
                    agent = agent_activities[0]
                    res = self.find_agents_by_name(agent.names[0])
                    if len(res) > 0:
                        log.debug('Found existing agent: {}'.format(res[0].names))
                        agent = res[0]
                    else:
                        agent.save()
                    av_entity.contributors.connect(
                        agent, {'activities': agent_activities[1]})
            elif r == 'rightholders':
                for rightholder in relationships[r]:
                    # look for existing rightholder
                    res = self.find_rightholder_by_name(rightholder.name2)
                    if res is not None:
                        log.debug(
                            'Found existing rightholder: {}'.format(res.name2))
                        rightholder = res
                    else:
                        rightholder.save()
                    av_entity.rightholders.connect(rightholder)

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
        av_entity = node.downcast()
        log.debug('creation instance of {}'.format(av_entity.__class__))
        video_format = av_entity.video_format.single()
        if video_format is not None:
            video_format.delete()

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

    def find_agents_by_name(self, name):
        log.debug('Find all agents with name: {}'.format(name))
        query = "MATCH (a:Agent) WHERE '{name}' in a.names RETURN a"
        results = self.graph.cypher(query.format(name=name))
        return [self.graph.Agent.inflate(row[0]) for row in results]

    def find_provider_by_identifier(self, pid, scheme):
        log.debug('Find provider by identifier [{}, {}]'.format(pid, scheme))
        # query = "MATCH (p:Provider {identifier: '{pid}', \
        # scheme:'{scheme}'}) RETURN p"
        # results = self.graph.Provider.cypher(
        #     query, {'pid': pid, 'scheme': scheme})
        # return [self.graph.Provider.inflate(row[0]) for row in results]
        return self.graph.Provider.nodes.get_or_none(
            identifier=pid, scheme=scheme)

    def find_rightholder_by_name(self, name):
        log.debug('Find rightholder by name: {}'.format(name))
        return self.graph.Rightholder.nodes.get_or_none(name2=name)
