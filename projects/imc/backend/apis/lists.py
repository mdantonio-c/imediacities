# -*- coding: utf-8 -*-

"""
Manage the lists of the researcher
"""
from flask import request
from restapi.confs import get_api_url
from restapi.confs import PRODUCTION
from restapi import decorators
from restapi.exceptions import RestApiException
from restapi.rest.definition import EndpointResource
from restapi.connectors.neo4j import graph_transactions
from restapi.utilities.logs import log
from restapi.utilities.htmlcodes import hcodes

import re

TARGET_PATTERN = re.compile("(item|shot):([a-z0-9-])+")

__author__ = "Giuseppe Trotta(g.trotta@cineca.it)"


class Lists(EndpointResource):

    labels = ['list']
    GET = {'/lists': {'summary': 'Get a list of the researcher', 'description': 'Returns all the list of a researcher.', 'parameters': [{'name': 'researcher', 'in': 'query', 'description': 'Researcher uuid', 'type': 'string'}, {'name': 'item', 'in': 'query', 'description': 'Item uuid (used to check whether the item belongs to the list or not)', 'type': 'string'}, {'name': 'includeNumberOfItems', 'in': 'query', 'type': 'boolean', 'default': False, 'allowEmptyValue': True}], 'responses': {'200': {'description': 'The list of the researcher.', 'schema': {'$ref': '#/definitions/List'}}, '401': {'description': 'This endpoint requires a valid authorization token'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'The requested list does not exist.'}}}, '/lists/<list_id>': {'summary': 'Get a list of the researcher', 'description': 'Returns all the list of a researcher.', 'parameters': [{'name': 'item', 'in': 'query', 'description': 'Item uuid (used to check whether the item belongs to the list or not)', 'type': 'string'}, {'name': 'includeNumberOfItems', 'in': 'query', 'type': 'boolean', 'default': False, 'allowEmptyValue': True}, {'name': 'researcher', 'in': 'query', 'description': 'Researcher uuid', 'type': 'string'}], 'responses': {'200': {'description': 'The list of the researcher.', 'schema': {'$ref': '#/definitions/List'}}, '401': {'description': 'This endpoint requires a valid authorization token'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'The requested list does not exist.'}}}}
    POST = {'/lists': {'summary': 'Create a new list', 'parameters': [{'name': 'list', 'in': 'body', 'description': 'The list to be created.', 'schema': {'$ref': '#/definitions/List'}}], 'responses': {'201': {'description': 'List created successfully.', 'schema': {'$ref': '#/definitions/List'}}, '400': {'description': 'There is no content present in the request body or the content is not valid for list.'}, '401': {'description': 'This endpoint requires a valid authorization token.'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '409': {'description': 'There is already a list with that name.'}}}}
    PUT = {'/lists/<list_id>': {'summary': 'Update a list', 'description': 'Update a list of the researcher', 'parameters': [{'name': 'updatedList', 'in': 'body', 'description': 'The updated list.', 'schema': {'$ref': '#/definitions/List'}}], 'responses': {'200': {'description': 'List updated successfully.'}, '400': {'description': 'There is no content present in the request body or the content is not valid for list.'}, '401': {'description': 'This endpoint requires a valid authorization token.'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'List does not exist.'}, '409': {'description': 'There is already another list with the same name among your lists.'}}}}
    DELETE = {'/lists/<list_id>': {'summary': 'Delete a list', 'description': 'Delete a list of the researcher.', 'responses': {'204': {'description': 'List deleted successfully.'}, '401': {'description': 'This endpoint requires a valid authorization token'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'List does not exist.'}}}}

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @decorators.auth.required(roles=['Researcher', 'admin_root'], required_roles='any')
    def get(self, list_id=None):
        """ Get all the list of a user or a certain list if an id is provided."""
        self.graph = self.get_service_instance('neo4j')

        iamadmin = self.auth.verify_admin()
        params = self.get_input()
        researcher = self.get_current_user() if not iamadmin else None
        r_uuid = params.get('researcher', None)
        if iamadmin and list_id is None and r_uuid is not None:
            try:
                researcher = self.graph.User.nodes.get(uuid=r_uuid)
            except self.graph.User.DoesNotExist:
                log.debug("Researcher with uuid {} does not exist", r_uuid)
                raise RestApiException(
                    "Please specify a valid researcher id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND,
                )
        user_match = ''
        optional_match = ''
        if researcher:
            user_match = "MATCH (n)-[:LST_BELONGS_TO]->(:User {{uuid:'{user}'}})".format(
                user=researcher.uuid
            )
            log.debug(
                "researcher: {name} {surname}".format(
                    name=researcher.name, surname=researcher.surname
                )
            )

        belong_item = params.get('item', None)
        nb_items = params.get('includeNumberOfItems')
        if isinstance(nb_items, str) and (nb_items == '' or nb_items.lower() == 'true'):
            nb_items = True
        elif type(nb_items) == bool:
            # do nothing
            pass
        else:
            nb_items = False
        if nb_items:
            optional_match = 'OPTIONAL MATCH (n)-[r:LST_ITEM]->(:ListItem)'
        if list_id is not None:
            try:
                res = self.graph.List.nodes.get(uuid=list_id)
            except self.graph.List.DoesNotExist:
                log.debug("List with uuid {} does not exist", list_id)
                raise RestApiException(
                    "Please specify a valid list id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND,
                )
            creator = res.creator.single()
            if not iamadmin and researcher.uuid != creator.uuid:
                raise RestApiException(
                    'You are not allowed to get a list that does not belong to you',
                    status_code=hcodes.HTTP_BAD_FORBIDDEN,
                )
            user_list = self.getJsonResponse(res)
            if iamadmin and researcher is None:
                user_list['creator'] = {
                    'uuid': creator.uuid,
                    'name': creator.name,
                    'surname': creator.surname,
                }
            if belong_item is not None:
                found = False
                for i in res.items.all():
                    if i.downcast().uuid == belong_item:
                        found = True
                        break
                user_list['belong'] = found
            if nb_items:
                user_list['nb_frames'] = len(res.items)
            return self.response(user_list)

        # request for multiple lists
        # offset, limit = self.get_paging()
        # offset -= 1
        # if offset < 0:
        #     raise RestApiException('Page number cannot be a negative value',
        #                            status_code=hcodes.HTTP_BAD_REQUEST)
        # if limit < 0:
        #     raise RestApiException('Page size cannot be a negative value',
        #                            status_code=hcodes.HTTP_BAD_REQUEST)
        count = (
            "MATCH (n:List)"
            " {match} "
            "RETURN COUNT(DISTINCT(n))".format(match=user_match)
        )
        # query = "MATCH (n:List)" \
        #         " {match} " \
        #         "RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
        #             match=user_match,
        #             offset=offset * limit,
        #             limit=limit)
        count_items = ', count(r)' if nb_items else ''
        query = (
            "MATCH (n:List) "
            "{match} "
            "{optional} "
            "RETURN DISTINCT(n){counter}".format(
                match=user_match, optional=optional_match, counter=count_items
            )
        )
        log.debug("query: {}", query)

        # get total number of lists
        numels = [row[0] for row in self.graph.cypher(count)][0]
        log.debug("Total number of lists: {0}", numels)

        data = []
        meta_response = {"totalItems": numels}
        results = self.graph.cypher(query)
        # for res in [self.graph.List.inflate(row[0]) for row in results]:
        for row in results:
            res = self.graph.List.inflate(row[0])
            user_list = self.getJsonResponse(res)
            if iamadmin and researcher is None:
                creator = res.creator.single()
                user_list['creator'] = {
                    'uuid': creator.uuid,
                    'name': creator.name,
                    'surname': creator.surname,
                }
            if belong_item is not None:
                for i in res.items.all():
                    if i.downcast().uuid == belong_item:
                        user_list['belong'] = True
                        break
            if nb_items:
                user_list['nb_items'] = row[1]
            data.append(user_list)
        return self.response(data, meta=meta_response)

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Researcher'])
    def post(self):
        """
        Create a new list.

        Only a researcher can create a list. Both name and description are
        mandatory. There can not be lists with the same name.
        """
        log.debug("create a new list")
        data = self.get_input()
        if len(data) == 0:
            raise RestApiException('Empty input', status_code=hcodes.HTTP_BAD_REQUEST)
        if 'name' not in data or not data['name'].strip():
            raise RestApiException(
                'Name is mandatory', status_code=hcodes.HTTP_BAD_REQUEST
            )
        if 'description' not in data or not data['description'].strip():
            raise RestApiException(
                'Description is mandatory', status_code=hcodes.HTTP_BAD_REQUEST
            )

        self.graph = self.get_service_instance('neo4j')
        user = self.get_current_user()
        # check if there is already a list with the same name belonging to the user.
        results = self.graph.cypher(
            "MATCH (l:List)-[:LST_BELONGS_TO]-(:User {{uuid:'{user}'}})"
            " WHERE l.name =~ '(?i){name}' return l".format(
                user=user.uuid, name=self.graph.sanitize_input(data['name'])
            )
        )
        duplicate = [self.graph.List.inflate(row[0]) for row in results]
        if duplicate:
            raise RestApiException(
                'There is already a list with the same name belonging to you',
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )

        created_list = self.graph.List(**data).save()
        # connect the creator
        created_list.creator.connect(user)
        log.debug("List created successfully. UUID {}", created_list.uuid)
        return self.response(
            self.getJsonResponse(created_list), code=hcodes.HTTP_OK_CREATED
        )

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Researcher'])
    def put(self, list_id):
        """ Update a list. """
        log.debug("Update list with uuid: {}", list_id)
        self.graph = self.get_service_instance('neo4j')
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            log.debug("List with uuid {} does not exist", list_id)
            raise RestApiException(
                "Please specify a valid list id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_current_user()
        creator = user_list.creator.single()
        if user.uuid != creator.uuid:
            raise RestApiException(
                'You cannot update an user list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        # validate input data
        data = self.get_input()
        if len(data) == 0:
            raise RestApiException('Empty input', status_code=hcodes.HTTP_BAD_REQUEST)
        if 'name' not in data or not data['name'].strip():
            raise RestApiException(
                'Name is mandatory', status_code=hcodes.HTTP_BAD_REQUEST
            )
        if 'description' not in data or not data['description'].strip():
            raise RestApiException(
                'Description is mandatory', status_code=hcodes.HTTP_BAD_REQUEST
            )

        # cannot update a list name if that name is already used for another list
        results = self.graph.cypher(
            "MATCH (l:List) WHERE l.uuid <> '{uuid}'"
            " MATCH (l)-[:LST_BELONGS_TO]-(:User {{uuid:'{user}'}})"
            " WHERE l.name =~ '(?i){name}' return l".format(
                uuid=list_id,
                user=user.uuid,
                name=self.graph.sanitize_input(data['name']),
            )
        )
        duplicate = [self.graph.List.inflate(row[0]) for row in results]
        if duplicate:
            raise RestApiException(
                'There is already another list with the same name [{}] among your lists'.format(
                    data['name']
                ),
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )
        # update the list
        user_list.name = data['name'].strip()
        user_list.description = data['description'].strip()
        updated_list = user_list.save()
        log.debug("List updated successfully. UUID {}", updated_list.uuid)
        return self.response(
            self.getJsonResponse(updated_list), code=hcodes.HTTP_OK_BASIC
        )

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Researcher', 'admin_root'], required_roles='any')
    def delete(self, list_id):
        """ Delete a list. """
        log.debug("delete list {}", list_id)
        if list_id is None:
            raise RestApiException(
                "Please specify a list id", status_code=hcodes.HTTP_BAD_REQUEST
            )
        self.graph = self.get_service_instance('neo4j')
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            log.debug("List with uuid {} does not exist", list_id)
            raise RestApiException(
                "Please specify a valid list id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        user = self.get_current_user()
        log.debug(
            'current user: {email} - {uuid}'.format(email=user.email, uuid=user.uuid)
        )
        iamadmin = self.auth.verify_admin()
        log.debug('current user is admin? {0}', iamadmin)

        creator = user_list.creator.single()
        if user.uuid != creator.uuid and not iamadmin:
            raise RestApiException(
                'You cannot delete an user list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        # delete the list
        user_list.delete()
        log.debug("List delete successfully. UUID {}", list_id)
        return self.empty_response()


class ListItems(EndpointResource):
    """ List of items in a list. """

    labels = ['list_items']
    GET = {
        '/lists/<list_id>/items/<item_id>': {'summary': 'List of items in a list.', 'responses': {'200': {'description': 'An list of items.'}, '401': {'description': 'This endpoint requires a valid authorzation token.'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'List does not exist.'}}, 'description': 'Get all the items of a list. The result supports paging.', 'parameters': [{'name': 'perpage', 'in': 'query', 'description': 'Number of lists returned', 'type': 'integer'}, {'name': 'currentpage', 'in': 'query', 'description': 'Page number', 'type': 'integer'}]}, 
        '/lists/<list_id>/items': {'summary': 'List of items in a list.', 'responses': {'200': {'description': 'An list of items.'}, '401': {'description': 'This endpoint requires a valid authorzation token.'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'List does not exist.'}}, 'description': 'Get all the items of a list. The result supports paging.', 'parameters': [{'name': 'perpage', 'in': 'query', 'description': 'Number of lists returned', 'type': 'integer'}, {'name': 'currentpage', 'in': 'query', 'description': 'Page number', 'type': 'integer'}]}
    }
    POST = {'/lists/<list_id>/items': {'summary': 'Add an item to a list.', 'parameters': [{'name': 'item', 'in': 'body', 'description': "Item to be added. It can be 'item' or 'shot'.", 'schema': {'required': ['target'], 'properties': {'target': {'type': 'string', 'pattern': '(item|shot):[a-z0-9-]+'}}}}], 'responses': {'204': {'description': 'Item added successfully.'}, '400': {'description': 'Bad request body or target node does not exist.'}, '401': {'description': 'This endpoint requires a valid authorization token.'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'List does not exist.'}, '409': {'description': 'The item is already connected to that list.'}}}}
    DELETE = {'/lists/<list_id>/items/<item_id>': {'summary': 'Delete an item from a list.', 'responses': {'204': {'description': 'Item deleted successfully.'}, '401': {'description': 'This endpoint requires a valid authorization token.'}, '403': {'description': 'The user is not authorized to perform this operation.'}, '404': {'description': 'List or item does not exist.'}}}}

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @decorators.auth.required(roles=['Researcher', 'admin_root'], required_roles='any')
    def get(self, list_id, item_id=None):
        """ Get all the items of a list or a certain item of that list if an
        item id is provided."""
        self.graph = self.get_service_instance('neo4j')
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            log.debug("List with uuid {} does not exist", list_id)
            raise RestApiException(
                "Please specify a valid list id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        # am I the owner of the list? (allowed also to admin)
        user = self.get_current_user()
        iamadmin = self.auth.verify_admin()
        creator = user_list.creator.single()
        if user.uuid != creator.uuid and not iamadmin:
            raise RestApiException(
                'You are not allowed to get a list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )
        if item_id is not None:
            log.debug(
                "Get item <{0}> of the list <{1}, {2}>".format(
                    item_id, user_list.uuid, user_list.name
                )
            )
            # Find item with uuid <item_id> in the user_list
            # res = user_list.items.search(uuid=item_id)
            results = self.graph.cypher(
                "MATCH (l:List {{uuid:'{uuid}'}})"
                " MATCH (l)-[:LST_ITEM]->(i:ListItem {{uuid:'{item}'}})"
                " RETURN i"
                "".format(uuid=list_id, item=item_id)
            )
            res = [self.graph.ListItem.inflate(row[0]) for row in results]
            if not res:
                raise RestApiException(
                    "Item <{0}> is not connected to the list <{1}, {2}>".format(
                        item_id, user_list.uuid, user_list.name
                    ),
                    status_code=hcodes.HTTP_BAD_NOTFOUND,
                )
            return self.response(self.get_list_item_response(res[0]))

        log.debug(
            "Get all the items of the list <{0}, {1}>".format(
                user_list.uuid, user_list.name
            )
        )
        # do we need pagination here?
        offset, limit = self.get_paging()
        offset -= 1
        log.debug("paging: offset {0}, limit {1}", offset, limit)
        if offset < 0:
            raise RestApiException(
                'Page number cannot be a negative value',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        if limit < 0:
            raise RestApiException(
                'Page size cannot be a negative value',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        data = []
        for list_item in user_list.items.all():
            data.append(self.get_list_item_response(list_item))
        return self.response(data)

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Researcher'])
    def post(self, list_id):
        """ Add an item to a list. """
        log.debug("Add an item to list {}", list_id)
        data = self.get_input()
        # validate data input
        if len(data) == 0:
            raise RestApiException('Empty input', status_code=hcodes.HTTP_BAD_REQUEST)
        if 'target' not in data or not data['target'].strip():
            raise RestApiException(
                'Target is mandatory', status_code=hcodes.HTTP_BAD_REQUEST
            )
        target = data['target']
        # check if the target is valid
        if not TARGET_PATTERN.match(target):
            raise RestApiException(
                'Invalid Target format', status_code=hcodes.HTTP_BAD_REQUEST
            )
        log.debug('Add item with target: {}', target)

        self.graph = self.get_service_instance('neo4j')
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            log.debug("List with uuid {} does not exist", list_id)
            raise RestApiException(
                "Please specify a valid list id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )

        # am I the creator of the list?
        user = self.get_current_user()
        creator = user_list.creator.single()
        if user.uuid != creator.uuid:
            raise RestApiException(
                'You cannot add an item to a list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )

        target_type, tid = target.split(':')
        log.debug('target type: {}, target id: {}', target_type, tid)
        targetNode = None
        if target_type == 'item':
            targetNode = self.graph.Item.nodes.get_or_none(uuid=tid)
        elif target_type == 'shot':
            targetNode = self.graph.Shot.nodes.get_or_none(uuid=tid)
        else:
            # this should never be reached
            raise RestApiException(
                'Invalid target type', status_code=hcodes.HTTP_NOT_IMPLEMENTED
            )
        if targetNode is None:
            raise RestApiException(
                'Target [' + target_type + ':' + tid + '] does not exist',
                status_code=hcodes.HTTP_BAD_REQUEST,
            )
        # check if the incoming target is already connected to the list
        if targetNode.lists.is_connected(user_list):
            raise RestApiException(
                'The item is already connected to the list <{0}, {1}>.'.format(
                    list_id, user_list.name
                ),
                status_code=hcodes.HTTP_BAD_CONFLICT,
            )
        # connect the target to the list
        user_list.items.connect(targetNode)
        log.debug(
            "Item {0} added successfully to list <{1}, {2}>".format(
                target, list_id, user_list.name
            )
        )
        # 204: return empty response (?)
        self.empty_response()

    @decorators.catch_errors()
    @decorators.catch_graph_exceptions
    @graph_transactions
    @decorators.auth.required(roles=['Researcher', 'admin_root'], required_roles='any')
    def delete(self, list_id, item_id):
        """ Delete an item from a list. """
        self.graph = self.get_service_instance('neo4j')
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            log.debug("List with uuid {} does not exist", list_id)
            raise RestApiException(
                "Please specify a valid list id", status_code=hcodes.HTTP_BAD_NOTFOUND
            )
        log.debug(
            "delete item <{0}> from the list <{1}, {2}>".format(
                item_id, user_list.uuid, user_list.name
            )
        )
        # am I the creator of the list? (allowed also to admin)
        user = self.get_current_user()
        iamadmin = self.auth.verify_admin()
        creator = user_list.creator.single()
        if user.uuid != creator.uuid and not iamadmin:
            raise RestApiException(
                'You are not allowed to delete an item from a list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN,
            )
        matched_item = None
        for list_item in user_list.items.all():
            item = list_item.downcast()
            if item.uuid == item_id:
                matched_item = item
                break
        if matched_item is None:
            raise RestApiException(
                "Item <{uuid}> does not belong the the list <{list_id}, {list_name}>".format(
                    uuid=item_id, list_id=user_list.uuid, list_name=user_list.name
                ),
                status_code=hcodes.HTTP_BAD_NOTFOUND,
            )
        # disconnect the item
        user_list.items.disconnect(matched_item)
        log.debug(
            "Item <{0}> remeved from the list <{1}, {2}>successfully.".format(
                item_id, user_list.uuid, user_list.name
            )
        )
        return self.empty_response()

    def get_list_item_response(self, list_item):
        # look at the most derivative class
        # expected list_item of type :Item or :Shot
        mdo = list_item.downcast()
        item = None
        if isinstance(mdo, self.graph.Item):
            item = mdo
        elif isinstance(mdo, self.graph.Shot):
            item = mdo.item.single()
        else:
            raise ValueError("Invalid ListItem instance.")
        creation = item.creation.single()
        if creation is None:
            raise ValueError(
                "Very strange. Item <{}}> with no metadata".format(item.uuid))
        creation = creation.downcast()

        res = self.getJsonResponse(mdo, max_relationship_depth=0)

        api_url = get_api_url(request, PRODUCTION)
        if isinstance(mdo, self.graph.Item):
            # always consider v2 properties if exists
            v2 = item.other_version.single()
            content_type = 'videos' if item.item_type == 'Video' else 'images'
            res['links']['content'] = (
                api_url
                + 'api/'
                + content_type
                + '/'
                + creation.uuid
                + '/content?type='
                + content_type[:-1]
            )
            res['links']['thumbnail'] = (
                api_url
                + 'api/'
                + content_type
                + '/'
                + creation.uuid
                + '/content?type=thumbnail&size=large'
                if item.item_type == 'Video' or v2 is None
                else api_url
                + 'api/'
                + content_type
                + '/'
                + creation.uuid
                + '/content?type='
                + content_type[:-1]
            )
            res['links']['webpage'] = (
                api_url + 'app/catalog/' + content_type + '/' + creation.uuid
            )
        else:
            # SHOT
            res['links']['content'] = (
                api_url + 'api/videos/' + creation.uuid + '/content?type=video'
            )
            res['links']['webpage'] = api_url + 'app/catalog/videos/' + creation.uuid
            res['links']['thumbnail'] = (
                api_url + 'api/shots/' + mdo.uuid + '?content=thumbnail'
            )
            # add some video item attributes
            res['item'] = {
                "digital_format": item.digital_format,
                "dimension": item.dimension,
                "duration": item.duration,
                "framerate": item.framerate,
            }

        res['creation_id'] = creation.uuid
        res['rights_status'] = creation.get_rights_status_display()
        for record_source in creation.record_sources.all():
            provider = record_source.provider.single()
            res['city'] = provider.city
            break
        # add title
        for idx, t in enumerate(creation.titles.all()):
            # get default
            if not idx:
                res["title"] = t.text
            # override with english text
            if t.language and t.language == 'en':
                res["title"] = t.text
        # add description
        for idx, desc in enumerate(creation.descriptions.all()):
            # get default
            if not idx:
                res["description"] = desc.text
            # override with english text
            if desc.language and desc.language == 'en':
                res["description"] = desc.text
        # add contributor
        for agent in creation.contributors.all():
            rel = creation.contributors.relationship(agent)
            if (
                item.item_type == 'Video'
                and agent.names
                and 'Director' in rel.activities
            ):
                # expected one in the list
                res["director"] = agent.names[0]
                break
            if (
                item.item_type == 'Image'
                and agent.names
                and 'Creator' in rel.activities
            ):
                # expected one in the list
                res["creator"] = agent.names[0]
                break
        # add production year
        if item.item_type == 'Image' and creation.date_created:
            res["production_year"] = creation.date_created[0]
        if item.item_type == 'Video' and creation.production_years:
            res["production_year"] = creation.production_years[0]
        # add video format
        if item.item_type == 'Video':
            video_format = creation.video_format.single()
            if video_format is not None:
                res['video_format'] = self.getJsonResponse(
                    video_format, max_relationship_depth=0
                )
        # add notes and links
        res["annotations"] = {}
        notes = mdo.annotation.search(annotation_type='DSC', private=False)
        if notes:
            res["annotations"]["notes"] = []
            for n in notes:
                # expected single body here
                note_text = n.bodies.single().downcast()
                res["annotations"]["notes"].append(
                    {"text": note_text.value, "language": note_text.language}
                )
        links = mdo.annotation.search(annotation_type='LNK', private=False)
        if links:
            res["annotations"]["links"] = []
            for l in links:
                link_text = l.bodies.single().downcast()
                # a link can have a ReferenceBody
                if not isinstance(link_text, self.graph.TextualBody):
                    continue
                res["annotations"]["links"].append(link_text.value)
            if not res["annotations"]["links"]:
                del res["annotations"]["links"]
        if not res["annotations"]:
            del res["annotations"]
        return res
