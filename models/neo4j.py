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

# Extension of User model for accounting in API login/logout
class User(UserBase):
    id = StringProperty(required=True, unique_index=True)
    name = StringProperty(required=True)
    surname = StringProperty(required=True)
    name_surname = StringProperty(required=True, unique_index=True)

    videos = RelationshipFrom('Video', 'IS_OWNED_BY', cardinality=ZeroOrMore)
    belongs_to = RelationshipTo('Group', 'BELONGS_TO')
    coordinator = RelationshipTo(
        'Group', 'PI_FOR', cardinality=ZeroOrMore)

    _fields_to_show = [
        "email", "name", "surname"
    ]
    _relationships_to_follow = [
        'belongs_to', 'roles'
    ]

    _input_schema = [
        {
            "key": "email",
            "type": "text",
            "required": "true",
            "label": "Email",
            "description": "Email",
        },
        {
            "key": "password",
            "type": "text",
            "required": "false",
            "label": "Password",
            "description": "Password",
        },
        {
            "key": "name",
            "type": "text",
            "required": "true",
            "label": "Name",
            "description": "Name",
        },
        {
            "key": "surname",
            "type": "text",
            "required": "true",
            "label": "Surname",
            "description": "Surname",
        },
        {
            "key": "group",
            "type": "autocomplete",
            "required": "true",
            "label": "Group",
            "description": "Select a group",
            "islink": "true",
            "model_key": "_belongs_to",
            "select_label": "shortname",
            "select_id": "id"
        },
    ]


class Group(StructuredNode):
    id = StringProperty(required=True, unique_index=True)
    fullname = StringProperty(required=True, unique_index=True)
    shortname = StringProperty(required=True, unique_index=True)

    members = RelationshipFrom(
        'User', 'BELONGS_TO', cardinality=ZeroOrMore)
    coordinator = RelationshipFrom(
        'User', 'PI_FOR', cardinality=ZeroOrMore)

    _fields_to_show = [
        "shortname", "fullname"
    ]
    _relationships_to_follow = [
        'coordinator', 'members'
    ]

    _input_schema = [
        {
            "key": "shortname",
            "type": "text",
            "required": "true",
            "label": "Short name",
            "description": "Short name"
        },
        {
            "key": "fullname",
            "type": "text",
            "required": "true",
            "label": "Full name",
            "description": "Full name"
        },
        {
            "key": "coordinator",
            "type": "select",
            "required": "true",
            "label": "Group coordinator",
            "description": "Select a coordinator",
            "islink": "true",
            "model_key": "_coordinator",
            "select_id": "id",
            "options": []
        }
    ]


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
