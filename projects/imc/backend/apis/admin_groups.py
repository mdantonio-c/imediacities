# -*- coding: utf-8 -*-

from restapi import decorators as decorate

from restapi.rest.definition import EndpointResource
from restapi.exceptions import RestApiException
from restapi.protocols.bearer import authentication
from restapi.flask_ext.flask_neo4j import graph_transactions
from restapi.decorators import catch_graph_exceptions
from restapi.utilities.htmlcodes import hcodes

# from restapi.utilities.logs import log

__author__ = "Mattia D'Antonio (m.dantonio@cineca.it)"


class AdminGroups(EndpointResource):

    # schema_expose = True
    labels = ['admin']
    GET = {'/admin/groups/<group_id>': {'summary': 'List of groups', 'responses': {'200': {'description': 'List of groups successfully retrieved'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}, '/admin/groups': {'summary': 'List of groups', 'responses': {'200': {'description': 'List of groups successfully retrieved'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}
    POST = {'/admin/groups': {'parameters': [{'name': 'shortname', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Short name', 'custom': {'label': 'Short name'}}, {'name': 'fullname', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Full name', 'custom': {'label': 'Full name'}}, {'name': 'coordinator', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Select a coordinator', 'custom': {'htmltype': 'select', 'label': 'Group coordinator', 'model_key': '_coordinator', 'select_id': 'id', 'islink': True}}], 'summary': 'Create a new group', 'responses': {'200': {'description': 'The uuid of the new group is returned'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}
    PUT = {'/admin/groups/<group_id>': {'parameters': [{'name': 'shortname', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Short name', 'custom': {'label': 'Short name'}}, {'name': 'fullname', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Full name', 'custom': {'label': 'Full name'}}, {'name': 'coordinator', 'in': 'formData', 'type': 'string', 'required': True, 'description': 'Select a coordinator', 'custom': {'htmltype': 'select', 'label': 'Group coordinator', 'model_key': '_coordinator', 'select_id': 'id', 'islink': True}}], 'summary': 'Modify a group', 'responses': {'200': {'description': 'Group successfully modified'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}
    DELETE = {'/admin/groups/<group_id>': {'summary': 'Delete a group', 'responses': {'200': {'description': 'Group successfully deleted'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}

    @decorate.catch_error()
    @catch_graph_exceptions
    @authentication.required(roles=['admin_root'])
    def get(self, id=None):

        self.graph = self.get_service_instance('neo4j')
        nodeset = self.graph.Group.nodes

        data = []
        if nodeset is not None:
            for n in nodeset.all():
                data.append(self.getJsonResponse(n))

        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    @authentication.required(roles=['admin_root'])
    def post(self):

        self.graph = self.get_service_instance('neo4j')

        v = self.get_input()
        if len(v) == 0:
            raise RestApiException('Empty input', status_code=hcodes.HTTP_BAD_REQUEST)

        schema = self.get_endpoint_custom_definition()

        if 'get_schema' in v:
            users = self.graph.User.nodes
            for idx, val in enumerate(schema):
                if val["name"] == "coordinator":
                    schema[idx]["enum"] = []
                    for n in users.all():
                        r = self.auth.get_roles_from_user(n)

                        can_coordinate = False
                        if self.auth.role_admin in r:
                            can_coordinate = True
                        elif 'local_admin' in r:
                            can_coordinate = True

                        if can_coordinate:

                            label = "{} {} ({})".format(n.name, n.surname, n.email)

                            schema[idx]["enum"].append({n.uuid: label})

            return self.force_response(schema)

        # INIT #
        properties = self.read_properties(schema, v)

        if 'coordinator' not in v:
            raise RestApiException(
                'Coordinator not found', status_code=hcodes.HTTP_BAD_REQUEST
            )

        coordinator = self.graph.User.nodes.get_or_none(uuid=v['coordinator'])

        if coordinator is None:
            raise RestApiException(
                'User not found', status_code=hcodes.HTTP_BAD_REQUEST
            )

        # GRAPH #
        group = self.graph.Group(**properties).save()
        # group.coordinator.connect(coordinator)

        return self.force_response(group.uuid)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    @authentication.required(roles=['admin_root'])
    def put(self, group_id=None):

        if group_id is None:

            raise RestApiException(
                "Please specify a group id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        schema = self.get_endpoint_custom_definition()
        self.graph = self.get_service_instance('neo4j')

        v = self.get_input()

        group = self.graph.Group.nodes.get_or_none(uuid=group_id)
        if group is None:
            raise RestApiException("Group not found")

        self.update_properties(group, schema, v)
        group.save()

        if 'coordinator' in v:

            coordinator = self.graph.User.nodes.get_or_none(uuid=v['coordinator'])

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
    @authentication.required(roles=['admin_root'])
    def delete(self, group_id=None):

        if group_id is None:

            raise RestApiException(
                "Please specify a group id", status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance('neo4j')

        group = self.graph.Group.nodes.get_or_none(uuid=group_id)
        if group is None:
            raise RestApiException("Group not found")

        group.delete()

        return self.empty_response()


class UserGroup(EndpointResource):

    labels = ['miscellaneous']
    GET = {'/group/<query>': {'summary': 'List of existing groups', 'responses': {'200': {'description': 'List of groups successfully retrieved'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}, '/group': {'summary': 'List of existing groups', 'responses': {'200': {'description': 'List of groups successfully retrieved'}, '401': {'description': 'This endpoint requires a valid authorization token'}}}}

    @decorate.catch_error()
    @catch_graph_exceptions
    @authentication.required()
    def get(self, query=None):

        self.graph = self.get_service_instance('neo4j')

        data = []

        if not self.auth.verify_admin():

            current_user = self.get_current_user()
            for g in current_user.belongs_to.all():
                data.append({"id": g.uuid, "shortname": g.shortname})
                return self.force_response(data)

        cypher = "MATCH (g:Group)"

        if query is not None:
            cypher += " WHERE g.shortname =~ '(?i).*{}.*'".format(query)

        cypher += " RETURN g ORDER BY g.shortname ASC"

        if query is None:
            cypher += " LIMIT 20"

        result = self.graph.cypher(cypher)
        for row in result:
            g = self.graph.Group.inflate(row[0])
            data.append({"id": g.uuid, "shortname": g.shortname})

        return self.force_response(data)
