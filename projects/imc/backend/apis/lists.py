# -*- coding: utf-8 -*-

"""
Manage the lists of the researcher
"""

from restapi import decorators as decorate
from restapi.services.neo4j.graph_endpoints import (GraphBaseOperations,
                                                    graph_transactions,
                                                    catch_graph_exceptions)
from utilities.logs import get_logger
from utilities import htmlcodes as hcodes

logger = get_logger(__name__)

__author__ = "Giuseppe Trotta(g.trotta@cineca.it)"


class Lists(GraphBaseOperations):

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, list_id=None):
        """ Get all the list of a user or a certain list if an id is provided."""
        self.graph = self.get_service_instance('neo4j')
        data = []
        # TODO
        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):
        """ Create a new list. """
        data = self.get_input()
        # check data input
        pass

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def put(self, list_id):
        """ Update a list. """
        pass

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, list_id):
        """ Delete a list. """
        pass


class ListItems(GraphBaseOperations):
    """ List of items in a list. """

    @decorate.catch_error()
    @catch_graph_exceptions
    def get(self, item_id=None):
        """ Get all the items of a list or a certain item of that list if an
        item id is provided."""
        self.graph = self.get_service_instance('neo4j')
        data = []
        # TODO
        return self.force_response(data)

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def post(self):
        """ Add an item to a list. """
        data = self.get_input()
        # check data input
        pass

    @decorate.catch_error()
    @catch_graph_exceptions
    @graph_transactions
    def delete(self, list_id):
        """ Delete an item from a list. """
        pass
