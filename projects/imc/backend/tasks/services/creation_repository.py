from datetime import datetime

import pytz
from neomodel.cardinality import CardinalityViolation
from restapi import decorators
from restapi.utilities.logs import log


class CreationRepository:
    """ """

    def __init__(self, graph):
        self.graph = graph

    @decorators.database_transaction
    def create_entity(self, properties, item, relationships, av=True):
        """
        Used to create both audio visual and NON audio visual entity.
        """

        # check if a creation already exists and delete it
        existing_creation = item.creation.single()
        if existing_creation is not None:
            log.debug("Creation already exists for current Item")
            creation_id = existing_creation.uuid
            if av:
                self.delete_av_entity(existing_creation)
            else:
                self.delete_non_av_entity(existing_creation)
            log.info("Existing creation [UUID:{0}] deleted", creation_id)
            # use the same uuid for the new replacing creation
            properties["uuid"] = creation_id

        entity = (
            self.graph.AVEntity(**properties).save()
            if av
            else self.graph.NonAVEntity(**properties).save()
        )
        # connect to item
        item.creation.connect(entity)
        # create/update digital_format in the item
        item.digital_format = item.dimension = None
        if digital_format := properties.get("digital_format"):
            item.digital_format = [None for _ in range(4)]
            item.digital_format[0] = digital_format.get("value")
            item.dimension = digital_format.get("size")
        item.save()

        # add relationships
        for r in relationships.keys():
            if r == "record_sources":
                # connect to record sources
                for rec_item in relationships[r]:
                    record_source = self.graph.RecordSource(**rec_item[0]).save()
                    entity.record_sources.connect(record_source)
                    # look for existing content provider
                    provider = self.find_provider_by_identifier(
                        rec_item[1]["identifier"], rec_item[1]["scheme"]
                    )
                    if provider is None:
                        provider = self.graph.Provider(**rec_item[1]).save()
                    record_source.provider.connect(provider)
            elif r == "titles":
                # connect to titles
                for title in relationships[r]:
                    # if 'relation' not in title:
                    #     title['relation'] = 'Original title'
                    title_node = self.graph.Title(**title).save()
                    entity.titles.connect(title_node)
            elif r == "keywords":
                # connect to keywords
                for props in relationships[r]:
                    keyword = self.graph.Keyword(**props).save()
                    entity.keywords.connect(keyword)
            elif r == "descriptions":
                for props in relationships[r]:
                    description = self.graph.Description(**props).save()
                    entity.descriptions.connect(description)
            elif r == "languages":
                # connect to languages
                for lang_usage in relationships[r]:
                    lang = self.graph.Language.nodes.get_or_none(code=lang_usage[0])
                    if lang is None:
                        lang = self.graph.Language(code=lang_usage[0]).save()
                    entity.languages.connect(lang, {"usage": lang_usage[1]})
            elif r == "coverages":
                for key, values in relationships[r].items():
                    # connect to coverages
                    if key == "temporal":
                        for props in values:
                            temporal_coverage = self.graph.TemporalCoverage(
                                **props
                            ).save()
                            entity.temporal_coverages.connect(temporal_coverage)
                    elif key == "spatial":
                        for props in values:
                            spatial_coverage = self.graph.SpatialCoverage(
                                **props
                            ).save()
                            entity.spatial_coverages.connect(spatial_coverage)
                    else:
                        log.warning(f"Coverage type <{key}> not managed")
            elif av and r == "production_countries":
                for country_reference in relationships[r]:
                    country = self.graph.Country.nodes.get_or_none(
                        code=country_reference[0]
                    )
                    if country is None:
                        country = self.graph.Country(code=country_reference[0]).save()
                    entity.production_countries.connect(
                        country, {"reference": country_reference[1]}
                    )
            elif av and r == "video_format" and relationships[r] is not None:
                video_format = self.graph.VideoFormat(**relationships[r]).save()
                entity.video_format.connect(video_format)
            elif not av and r == "3d-format" and relationships[r] is not None:
                three_dim_format = self.graph.ThreeDimFormat(**relationships[r]).save()
                item.three_dim_format.connect(three_dim_format)
            elif r == "agents":
                for agent_activities in relationships[r]:
                    # look for existing agents
                    props = agent_activities[0]
                    res = self.find_agents_by_name(props["names"][0])
                    if len(res) > 0:
                        log.debug("Found existing agent: {}", res[0].names)
                        agent = res[0]
                    else:
                        agent = self.graph.Agent(**props).save()
                    entity.contributors.connect(
                        agent, {"activities": agent_activities[1]}
                    )
            elif r == "rightholders":
                for props in relationships[r]:
                    # look for existing rightholder
                    rightholder = self.find_rightholder_by_name(props["name"])
                    if rightholder is None:
                        rightholder = self.graph.Rightholder(**props).save()
                    else:
                        log.debug("Found existing rightholder: {}", rightholder.name)
                    entity.rightholders.connect(rightholder)

        return entity

    def __delete_entity(self, node):
        try:
            for rc in node.record_sources.all():
                rc.delete()
        except CardinalityViolation:
            pass
        try:
            for title in node.titles.all():
                title.delete()
        except CardinalityViolation:
            pass
        try:
            for description in node.descriptions.all():
                description.delete()
        except CardinalityViolation:
            pass
        for keyword in node.keywords.all():
            keyword.delete()
        for coverage in node.spatial_coverages:
            coverage.delete()
        for coverage in node.temporal_coverages:
            coverage.delete()

    def delete_av_entity(self, node):
        self.__delete_entity(node)
        av_entity = node.downcast()
        uuid = av_entity.uuid
        video_format = av_entity.video_format.single()
        if video_format is not None:
            video_format.delete()
        av_entity.delete()
        log.debug("Delete AVEntity with uuid {}", uuid)

    def delete_non_av_entity(self, node):
        self.__delete_entity(node)
        non_av_entity = node.downcast()
        uuid = non_av_entity.uuid
        item = non_av_entity.item.single()
        three_dim_format = item.three_dim_format.single()
        if three_dim_format is not None:
            three_dim_format.delete()
        non_av_entity.delete()
        log.debug("Delete NonAVEntity with uuid {}", uuid)

    def search_item_by_term(self, term, item_type):
        """
        Search all types of items and see whether some attributes matches the
        value provided by the user.
        """
        log.debug("Searching for Items with term = ", term)
        pass

    def find_agents_by_name(self, name):
        log.debug("Find all agents with name: {}", name)
        name = self.graph.sanitize_input(name)
        query = "MATCH (a:Agent) WHERE '{name}' in a.names RETURN a"
        results = self.graph.cypher(query.format(name=name))
        return [self.graph.Agent.inflate(row[0]) for row in results]

    def find_provider_by_identifier(self, pid, scheme):
        log.debug("Find provider by identifier [{}, {}]", pid, scheme)
        # query = "MATCH (p:Provider {identifier: '{pid}', \
        # scheme:'{scheme}'}) RETURN p"
        # results = self.graph.Provider.cypher(
        #     query, {'pid': pid, 'scheme': scheme})
        # return [self.graph.Provider.inflate(row[0]) for row in results]
        return self.graph.Provider.nodes.get_or_none(identifier=pid, scheme=scheme)

    def find_rightholder_by_name(self, name):
        log.debug("Find rightholder by name: {}", name)
        return self.graph.Rightholder.nodes.get_or_none(name=name)

    def item_belongs_to_user(self, item, user):
        group = user.belongs_to.single()
        if group is None:
            return False
        return item.ownership.is_connected(group)

    def move_video_under_revision(self, item, user):
        item.revision.connect(user, {"when": datetime.now(pytz.utc), "state": "W"})

    def exit_video_under_revision(self, item):
        item.revision.disconnect_all()

    def is_video_under_revision(self, item):
        return False if item.revision.single() is None else True

    def is_revision_assigned_to_user(self, item, user):
        return item.revision.is_connected(user)

    def get_right_status(self, entity_id):
        entity = self.graph.Creation.nodes.get_or_none(uuid=entity_id)
        if entity is not None:
            return entity.rights_status

    def publicly_accessible(self, entity_id):
        entity = self.graph.Creation.nodes.get_or_none(uuid=entity_id)
        item = entity.item.single()
        return item.public_access

    def get_belonging_city(self, item):
        log.debug("Look for belonging city for item {}", item.uuid)
        query = (
            "MATCH (i:Item {{uuid:'{item_id}'}})-[:CREATION]-()"
            "-[:RECORD_SOURCE]->()-[:PROVIDED_BY]->(p:Provider) "
            "RETURN p.city"
        )
        results = self.graph.cypher(query.format(item_id=item.uuid))
        return [row[0] for row in results][0] if results else None
