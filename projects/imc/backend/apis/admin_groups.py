# -*- coding: utf-8 -*-

from restapi import decorators as decorate

from restapi.services.neo4j.graph_endpoints import GraphBaseOperations
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import graph_transactions
from restapi.services.neo4j.graph_endpoints import catch_graph_exceptions
from utilities import htmlcodes as hcodes

from utilities.logs import get_logger
logger = get_logger(__name__)

__author__ = "Mattia D'Antonio (m.dantonio@cineca.it)"


class AdminGroups(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, id=None):

        self.initGraph()
        nodeset = self.graph.Group.nodes

        data = []
        if nodeset is not None:
            for n in nodeset.all():
                data.append(self.getJsonResponse(n))

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):

        self.initGraph()

        v = self.get_input()
        if len(v) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)

        schema = self.get_endpoint_custom_definition()

        if 'get_schema' in v:
            users = self.graph.User.nodes
            for idx, val in enumerate(schema):
                if val["name"] == "coordinator":
                    schema[idx]["enum"] = []
                    for n in users.all():
                        schema[idx]["enum"].append(
                            {
                                n.uuid: n.email
                            }
                        )

            return self.force_response(schema)

        # INIT #
        properties = self.read_properties(schema, v)

        if 'coordinator' not in v:
            raise RestApiException(
                'Coordinator not found', status_code=hcodes.HTTP_BAD_REQUEST)

        coordinator = self.graph.User.nodes.get_or_none(uuid=v['coordinator'])
        # coordinator = self.getNode(
        #     self.graph.User, v['coordinator'], field='uuid')

        if coordinator is None:
            raise RestApiException(
                'User not found', status_code=hcodes.HTTP_BAD_REQUEST)

        # GRAPH #
        group = self.graph.Group(**properties).save()
        # group.coordinator.connect(coordinator)

        return self.force_response(group.uuid)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def put(self, group_id=None):

        if group_id is None:

            raise RestApiException(
                "Please specify a group id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        schema = self.get_endpoint_custom_definition()
        self.initGraph()

        v = self.get_input()

        group = self.graph.Group.nodes.get_or_none(uuid=group_id)
        # group = self.getNode(self.graph.Group, group_id, field='uuid')
        if group is None:
            raise RestApiException("Group not found")

        self.update_properties(group, schema, v)
        group.save()

        if 'coordinator' in v:

            coordinator = self.graph.User.nodes.get_or_none(
                uuid=v['coordinator'])
            # coordinator = self.getNode(
            #     self.graph.User, v['coordinator'], field='uuid')

            p = None
            for p in group.coordinator.all():
                if p == coordinator:
                    continue

            if p is None:
                group.coordinator.connect(coordinator)
            else:
                group.coordinator.reconnect(p, coordinator)

        return self.empty_response()

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, group_id=None):

        if group_id is None:

            raise RestApiException(
                "Please specify a group id",
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()

        group = self.graph.Group.nodes.get_or_none(uuid=group_id)
        # group = self.getNode(self.graph.Group, group_id, field='uuid')
        if group is None:
            raise RestApiException("Group not found")

        group.delete()

        return self.empty_response()


class UserGroup(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, query=None):

        self.initGraph()

        data = []
        cypher = "MATCH (g:Group)"

        if query is not None:
            cypher += " WHERE g.shortname =~ '(?i).*%s.*'" % query

        cypher += " RETURN g ORDER BY g.shortname ASC"

        if query is None:
            cypher += " LIMIT 20"

        result = self.graph.cypher(cypher)
        for row in result:
            g = self.graph.Group.inflate(row[0])
            data.append({"id": g.uuid, "shortname": g.shortname})

        return self.force_response(data)
