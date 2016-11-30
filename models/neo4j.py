# -*- coding: utf-8 -*-

"""
Graph DB abstraction from neo4j server.
These are custom models!

VERY IMPORTANT!
Imports and models have to be defined/used AFTER normal Graphdb connection.
"""

from __future__ import absolute_import
from neomodel import StringProperty, IntegerProperty, DateTimeProperty, \
    StructuredNode, RelationshipTo, RelationshipFrom, \
    ZeroOrMore

from ..neo4j import User as UserBase

import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


##############################################################################
# MODELS
##############################################################################


# Extension of User model
class User(UserBase):
    videos = RelationshipFrom('Video', 'IS_OWNED_BY', cardinality=ZeroOrMore)


class Video(StructuredNode):
    uuid = StringProperty(required=True, unique_index=True)
    created = DateTimeProperty(required=True)
    modified = DateTimeProperty(required=True)
    filename = StringProperty(required=True)

    title = StringProperty()
    description = StringProperty()
    duration = IntegerProperty()
    ownership = RelationshipTo('User', 'IS_OWNED_BY', cardinality=ZeroOrMore)
    annotation = RelationshipTo('Annotation', 'IS_ANNOTATED_BY')


class Annotation(StructuredNode):
    uuid = StringProperty(required=True, unique_index=True)
    key = StringProperty(equired=True)
    value = StringProperty(equired=True)
    video = RelationshipFrom('Video', 'IS_ANNOTATED_BY')
