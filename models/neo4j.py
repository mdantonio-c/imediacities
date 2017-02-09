# -*- coding: utf-8 -*-

"""
Graph DB abstraction from neo4j server.
These are custom models!

VERY IMPORTANT!
Imports and models have to be defined/used AFTER normal Graphdb connection.
"""

from __future__ import absolute_import
from ...neo4j.models import \
    StringProperty, IntegerProperty, \
    IdentifiedNode, TimestampedNode, RelationshipTo, RelationshipFrom
from neomodel import ZeroOrMore

from ..neo4j import User as UserBase

import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)


##############################################################################
# MODELS
##############################################################################

# Extension of User model for accounting in API login/logout
class User(UserBase):
    # name_surname = StringProperty(required=True, unique_index=True)

    videos = RelationshipFrom('Video', 'IS_OWNED_BY', cardinality=ZeroOrMore)
    belongs_to = RelationshipTo('Group', 'BELONGS_TO', show=True)
    coordinator = RelationshipTo(
        'Group', 'PI_FOR', cardinality=ZeroOrMore)


class Group(IdentifiedNode):
    fullname = StringProperty(required=True, unique_index=True, show=True)
    shortname = StringProperty(required=True, unique_index=True, show=True)

    members = RelationshipFrom(
        'User', 'BELONGS_TO', cardinality=ZeroOrMore, show=True)
    coordinator = RelationshipFrom(
        'User', 'PI_FOR', cardinality=ZeroOrMore, show=True)


class Video(TimestampedNode):
    filename = StringProperty(required=True, show=True)

    title = StringProperty()
    description = StringProperty()
    duration = IntegerProperty()
    ownership = RelationshipTo(
        'User', 'IS_OWNED_BY', cardinality=ZeroOrMore, show=True)
    annotation = RelationshipTo('Annotation', 'IS_ANNOTATED_BY')


class Annotation(IdentifiedNode):
    key = StringProperty(required=True)
    value = StringProperty(required=True)
    video = RelationshipFrom('Video', 'IS_ANNOTATED_BY')
