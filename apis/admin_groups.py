# -*- coding: utf-8 -*-

from .. import decorators as decorate
from ...auth import authentication

from ..services.neo4j.graph_endpoints import GraphBaseOperations
from ..services.neo4j.graph_endpoints import myGraphError
from ..services.neo4j.graph_endpoints import returnError
from ..services.neo4j.graph_endpoints import graph_transactions
from ..services.neo4j.graph_endpoints import catch_graph_exceptions
from commons import htmlcodes as hcodes
from restapi.confs import config

from commons.logs import get_logger
logger = get_logger(__name__)

__author__ = "Mattia D'Antonio (m.dantonio@cineca.it)"


class AdminGroups(GraphBaseOperations):

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @authentication.authorization_required(roles=[config.ROLE_ADMIN])
    # @decorate.apimethod
    def get(self, id=None):

        self.initGraph()
        nodeset = self.graph.Group.nodes

        data = []
        if nodeset is not None:
            for n in nodeset.all():
                data.append(self.getJsonResponse(n))

        return self.force_response(data)

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    @authentication.authorization_required(roles=[config.ROLE_ADMIN])
    # @decorate.apimethod
    def post(self):

        self.initGraph()

        v = self.get_input()
        if len(v) == 0:
            schema = self.graph.Group._input_schema.copy()
            return self.force_response(schema)

        # INIT #
        properties = self.readProperty(self.graph.Group._input_schema, v)

        if 'coordinator' not in v:
            raise myGraphError(
                'Coordinator not found', status_code=hcodes.HTTP_BAD_REQUEST)

        coordinator = self.getNode(
            self.graph.User, v['coordinator'], field='id')

        if coordinator is None:
            raise myGraphError(
                'User not found', status_code=hcodes.HTTP_BAD_REQUEST)

        # GRAPH #
        group = self.graph.createNode(self.graph.Group, properties)
        group.coordinator.connect(coordinator)

        return self.force_response(group.id)

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    @authentication.authorization_required(roles=[config.ROLE_ADMIN])
    # @decorate.apimethod
    def put(self, group_id=None):

        if group_id is None:

            return returnError(
                self,
                label="Invalid request",
                error="Please specify a group id",
                code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()

        v = self.get_input()

        group = self.getNode(self.graph.Group, group_id, field='id')
        if group is None:
            raise myGraphError(self.GROUP_NOT_FOUND)

        self.updateProperties(group, self.graph.Group._input_schema, v)
        group.save()

        if 'coordinator' in v:

            coordinator = self.getNode(
                self.graph.User, v['coordinator'], field='id')

            p = None
            for p in group.coordinator.all():
                if p == coordinator:
                    continue

            if p is None:
                group.coordinator.connect(coordinator)
            else:
                group.coordinator.reconnect(p, coordinator)

        return self.empty_response()

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    @authentication.authorization_required(roles=[config.ROLE_ADMIN])
    # @decorate.apimethod
    def delete(self, group_id=None):

        if group_id is None:

            return returnError(
                self,
                label="Invalid request",
                error="Please specify a group id",
                code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()

        group = self.getNode(self.graph.Group, group_id, field='id')
        if group is None:
            raise myGraphError(self.GROUP_NOT_FOUND)

        group.delete()

        return self.empty_response()
