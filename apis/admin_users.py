# -*- coding: utf-8 -*-

import random
import string
from .. import decorators as decorate
from ...auth import authentication

from ..services.neo4j.graph_endpoints import GraphBaseOperations
from ..services.neo4j.graph_endpoints import myGraphError
from ..services.neo4j.graph_endpoints import returnError
from ..services.neo4j.graph_endpoints import graph_transactions
from ..services.neo4j.graph_endpoints import catch_graph_exceptions
from commons import htmlcodes as hcodes
from commons.services.uuid import getUUID
from restapi.confs import config
from restapi.resources.services.authentication import BaseAuthentication

from commons.logs import get_logger
logger = get_logger(__name__)

__author__ = "Mattia D'Antonio (m.dantonio@cineca.it)"


class AdminUsers(GraphBaseOperations):

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @authentication.authorization_required(roles=[config.ROLE_ADMIN])
    # @decorate.apimethod
    def get(self, id=None):

        self.initGraph()
        nodeset = self.graph.User.nodes

        data = []
        for n in nodeset.all():
            user = self.getJsonResponse(n, max_relationship_depth=2)
            data.append(user)

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
            return self.graph.User._input_schema

        # INIT #
        properties = self.readProperty(self.graph.User._input_schema, v)

        groups = self.parseAutocomplete(v, 'group', id_key='id')

        if groups is None:
            raise myGraphError(
                'Group not found', status_code=hcodes.HTTP_BAD_REQUEST)

        group_id = groups.pop()

        group = self.getNode(self.graph.Group, group_id, field='id')

        if group is None:
            raise myGraphError(
                'Group not found', status_code=hcodes.HTTP_BAD_REQUEST)

        rand = random.SystemRandom()
        charset = string.ascii_uppercase + string.digits

        cert_pass = ""
        for _ in range(12):
            cert_pass += rand.choice(charset)

        # GRAPH #
        properties["uuid"] = getUUID()
        properties["authmethod"] = "credentials"
        # if "password" in properties:
        properties["password"] = \
            BaseAuthentication.hash_password(properties["password"])
        properties["name_surname"] = \
            self.createUniqueIndex(properties["name"], properties["surname"])
        user = self.graph.createNode(self.graph.User, properties)
        user.belongs_to.connect(group)

        return self.force_response(user.id)

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    @authentication.authorization_required(roles=[config.ROLE_ADMIN])
    # @decorate.apimethod
    def put(self, user_id=None):

        if user_id is None:

            return returnError(
                self,
                label="Invalid request",
                error="Please specify a user id",
                code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()

        v = self.get_input()

        user = self.getNode(self.graph.User, user_id, field='id')
        if user is None:
            raise myGraphError(self.USER_NOT_FOUND)

        if "password" in v and v["password"] == "":
            del v["password"]
        else:
            v["password"] = BaseAuthentication.hash_password(v["password"])

        self.updateProperties(user, self.graph.User._input_schema, v)
        user.name_surname = self.createUniqueIndex(user.name, user.surname)
        user.save()

        groups = self.parseAutocomplete(v, 'group', id_key='id')

        if groups is not None:
            group_id = groups.pop()

            group = self.getNode(self.graph.Group, group_id, field='id')

            for p in user.belongs_to.all():
                if p == group:
                    continue

            user.belongs_to.reconnect(p, group)

        return self.empty_response()

    @decorate.catch_error(
        exception=Exception, exception_label=None, catch_generic=False)
    @catch_graph_exceptions
    @graph_transactions
    @authentication.authorization_required(roles=[config.ROLE_ADMIN])
    # @decorate.apimethod
    def delete(self, user_id=None):

        if user_id is None:

            return returnError(
                self,
                label="Invalid request",
                error="Please specify a user id",
                code=hcodes.HTTP_BAD_REQUEST)

        self.initGraph()

        user = self.getNode(self.graph.User, user_id, field='id')
        if user is None:
            raise myGraphError(self.USER_NOT_FOUND)

        user.delete()

        return self.empty_response()
