# -*- coding: utf-8 -*-

"""
Manage the lists of the researcher
"""

from restapi import decorators as decorate
from restapi.exceptions import RestApiException
from restapi.services.neo4j.graph_endpoints import (GraphBaseOperations,
                                                    graph_transactions,
                                                    catch_graph_exceptions)
from utilities.logs import get_logger
from utilities import htmlcodes as hcodes

import re
TARGET_PATTERN = re.compile("(item|shot):([a-z0-9-])+")

logger = get_logger(__name__)

__author__ = "Giuseppe Trotta(g.trotta@cineca.it)"


class Lists(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, list_id=None):
        """ Get all the list of a user or a certain list if an id is provided."""
        self.graph = self.get_service_instance('neo4j')

        iamadmin = self.auth.verify_admin()
        params = self.get_input()
        researcher = self.get_current_user() if not iamadmin else None
        r_uuid = params.get('researcher', None)
        if iamadmin and list_id is not None and r_uuid is not None:
            try:
                researcher = self.graph.User.nodes.get(uuid=r_uuid)
            except self.graph.User.DoesNotExist:
                logger.debug("Researcher with uuid %s does not exist" % r_uuid)
                raise RestApiException(
                    "Please specify a valid researcher id",
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
        user_match = ''
        if researcher:
            user_match = "MATCH (n)-[:LST_BELONGS_TO]->(:User {{uuid:'{user}'}})".format(
                         user=researcher.uuid)
            logger.debug("researcher: {name} {surname}".format(
                name=researcher.name, surname=researcher.surname))

        offset, limit = self.get_paging()
        offset -= 1
        logger.debug("paging: offset {0}, limit {1}".format(offset, limit))
        if offset < 0:
            raise RestApiException('Page number cannot be a negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)
        if limit < 0:
            raise RestApiException('Page size cannot be a negative value',
                                   status_code=hcodes.HTTP_BAD_REQUEST)
        single_match = ('' if list_id is None
                        else " {{uuid:'{0}'}}".format(
                            self.graph.sanitize_input(list_id)))
        count = "MATCH (n:List{single})" \
                " {match} " \
                "RETURN COUNT(DISTINCT(n))".format(
                    match=user_match,
                    single=single_match)
        # logger.debug("count query: %s" % count)
        query = "MATCH (n:List{single})" \
                " {match} " \
                "RETURN DISTINCT(n) SKIP {offset} LIMIT {limit}".format(
                    match=user_match,
                    single=single_match,
                    offset=offset * limit,
                    limit=limit)
        # logger.debug("query: %s" % query)

        # get total number of lists
        numels = [row[0] for row in self.graph.cypher(count)][0]
        logger.debug("Total number of lists: {0}".format(numels))

        data = []
        results = self.graph.cypher(query)
        for res in [self.graph.List.inflate(row[0]) for row in results]:
            user_list = self.getJsonResponse(res)
            if iamadmin and researcher is None:
                creator = res.creator.single()
                user_list['creator'] = {
                    'uuid': creator.uuid,
                    'name': creator.name,
                    'surname': creator.surname
                }
            data.append(user_list)
        if list_id is not None:
            if not data:
                raise RestApiException(
                    "List not found for id {}".format(list_id),
                    status_code=hcodes.HTTP_BAD_NOTFOUND)
            # return single result as an object
            data = data[0]
        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):
        """
        Create a new list.

        Only a researcher can create a list. Both name and description are
        mandatory. There can not be lists with the same name.
        """
        logger.debug("create a new list")
        data = self.get_input()
        if len(data) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)
        if 'name' not in data or not data['name'].strip():
            raise RestApiException(
                'Name is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)
        if 'description' not in data or not data['description'].strip():
            raise RestApiException(
                'Description is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')
        user = self.get_current_user()
        # check if there is already a list with the same name belonging to the user.
        results = self.graph.cypher("MATCH (l:List)-[:LST_BELONGS_TO]-(:User {{uuid:'{user}'}})"
                                    " WHERE l.name =~ '(?i){name}' return l"
                                    .format(user=user.uuid, name=self.graph.sanitize_input(data['name'])))
        duplicate = [self.graph.List.inflate(row[0]) for row in results]
        if duplicate:
            raise RestApiException(
                'There is already a list with the same name belonging to you',
                status_code=hcodes.HTTP_BAD_CONFLICT)

        created_list = self.graph.List(**data).save()
        # connect the creator
        created_list.creator.connect(user)
        logger.debug("List created successfully. UUID {}"
                     .format(created_list.uuid))
        return self.force_response(
            self.getJsonResponse(created_list), code=hcodes.HTTP_OK_CREATED)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def put(self, list_id):
        """ Update a list. """
        logger.debug("Update list with uuid: %s", list_id)
        self.graph = self.get_service_instance('neo4j')
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            logger.debug("List with uuid %s does not exist" % list_id)
            raise RestApiException(
                "Please specify a valid list id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()
        creator = user_list.creator.single()
        if user.uuid != creator.uuid:
            raise RestApiException(
                'You cannot update an user list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        # validate input data
        data = self.get_input()
        if len(data) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)
        if 'name' not in data or not data['name'].strip():
            raise RestApiException(
                'Name is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)
        if 'description' not in data or not data['description'].strip():
            raise RestApiException(
                'Description is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)

        # cannot update a list name if that name is already used for another list
        results = self.graph.cypher("MATCH (l:List) WHERE l.uuid <> '{uuid}'"
                                    " MATCH (l)-[:LST_BELONGS_TO]-(:User {{uuid:'{user}'}})"
                                    " WHERE l.name =~ '(?i){name}' return l"
                                    .format(uuid=list_id,
                                            user=user.uuid,
                                            name=self.graph.sanitize_input(data['name'])))
        duplicate = [self.graph.List.inflate(row[0]) for row in results]
        if duplicate:
            raise RestApiException(
                'There is already another list with the same name [{}] among your lists'.format(data['name']),
                status_code=hcodes.HTTP_BAD_CONFLICT)
        # update the list
        user_list.name = data['name'].strip()
        user_list.description = data['description'].strip()
        updated_list = user_list.save()
        logger.debug("List updated successfully. UUID {}"
                     .format(updated_list.uuid))
        return self.force_response(
            self.getJsonResponse(updated_list), code=hcodes.HTTP_OK_BASIC)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, list_id):
        """ Delete a list. """
        logger.debug("delete list %s" % list_id)
        if list_id is None:
            raise RestApiException(
                "Please specify a list id",
                status_code=hcodes.HTTP_BAD_REQUEST)
        self.graph = self.get_service_instance('neo4j')
        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            logger.debug("List with uuid %s does not exist" % list_id)
            raise RestApiException(
                "Please specify a valid list id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        user = self.get_current_user()
        logger.debug('current user: {email} - {uuid}'.format(
            email=user.email, uuid=user.uuid))
        iamadmin = self.auth.verify_admin()
        logger.debug('current user is admin? {0}'.format(iamadmin))

        creator = user_list.creator.single()
        if user.uuid != creator.uuid and not iamadmin:
            raise RestApiException(
                'You cannot delete an user list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        # delete the list
        user_list.delete()
        logger.debug("List delete successfully. UUID {}"
                     .format(list_id))
        return self.empty_response()


class ListItems(GraphBaseOperations):
    """ List of items in a list. """

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, list_id, item_id=None):
        """ Get all the items of a list or a certain item of that list if an
        item id is provided."""
        self.graph = self.get_service_instance('neo4j')
        data = []
        # TODO
        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self, list_id):
        """ Add an item to a list. """
        logger.debug("Add an item to list %s" % list_id)
        data = self.get_input()
        # validate data input
        if len(data) == 0:
            raise RestApiException(
                'Empty input',
                status_code=hcodes.HTTP_BAD_REQUEST)
        if 'target' not in data or not data['target'].strip():
            raise RestApiException(
                'Target is mandatory',
                status_code=hcodes.HTTP_BAD_REQUEST)
        target = data['target']
        logger.debug('Add item with target: {}'.format(target))
        # check if the target is valid
        if not TARGET_PATTERN.match(target):
            raise RestApiException(
                'Invalid Target format',
                status_code=hcodes.HTTP_BAD_REQUEST)

        self.graph = self.get_service_instance('neo4j')

        try:
            user_list = self.graph.List.nodes.get(uuid=list_id)
        except self.graph.List.DoesNotExist:
            logger.debug("List with uuid %s does not exist" % list_id)
            raise RestApiException(
                "Please specify a valid list id",
                status_code=hcodes.HTTP_BAD_NOTFOUND)

        # am I the creator of the list?
        user = self.get_current_user()
        creator = user_list.creator.single()
        if user.uuid != creator.uuid:
            raise RestApiException(
                'You cannot add an item to a list that does not belong to you',
                status_code=hcodes.HTTP_BAD_FORBIDDEN)

        target_type, tid = target.split(':')
        logger.debug('target type: {}, target id: {}'.format(target_type, tid))
        targetNode = None
        if target_type == 'item':
            targetNode = self.graph.Item.nodes.get_or_none(uuid=tid)
        elif target_type == 'shot':
            targetNode = self.graph.Shot.nodes.get_or_none(uuid=tid)
        else:
            # this should never be reached
            raise RestApiException(
                'Invalid target type',
                status_code=hcodes.HTTP_NOT_IMPLEMENTED)
        if targetNode is None:
            raise RestApiException(
                'Target [' + target_type + ':' + tid + '] does not exist',
                status_code=hcodes.HTTP_BAD_REQUEST)
        # TODO
        user_list.items.connect(targetNode)
        logger.debug("Item {} added successfully to list {}"
                     .format(target, list_id))
        # 204: Item added successfully.
        self.empty_response()

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, list_id, item_id):
        """ Delete an item from a list. """
        pass
