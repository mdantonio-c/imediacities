# -*- coding: utf-8 -*-

"""
Graph DB abstraction from neo4j server.
These are custom models!

VERY IMPORTANT!
Imports and models have to be defined/used AFTER normal Graphdb connection.
"""

from __future__ import absolute_import
from ...neo4j.models import \
    StringProperty, IntegerProperty, FloatProperty, DateTimeProperty, \
    StructuredNode, IdentifiedNode, TimestampedNode, RelationshipTo, RelationshipFrom
from neomodel import ZeroOrMore, OneOrMore, ZeroOrOne, One

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
    stage_files = RelationshipFrom(
        'Stage', 'IS_OWNED_BY', cardinality=ZeroOrMore, show=True)


class Stage(TimestampedNode):
    filename = StringProperty(required=True, show=True)
    path = StringProperty(required=True, unique_index=True, show=True)
    status = StringProperty(show=True)
    status_message = StringProperty(show=True)
    task_id = StringProperty(show=True)

    ownership = RelationshipTo(
        'Group', 'IS_OWNED_BY', cardinality=ZeroOrMore, show=True)
    video = RelationshipFrom('Video', 'VIDEO', cardinality=One)


class Video(TimestampedNode):
    title = StringProperty()
    description = StringProperty()
    duration = IntegerProperty()
    ownership = RelationshipTo(
        'Group', 'IS_OWNED_BY', cardinality=ZeroOrMore, show=True)
    item = RelationshipTo(
        'Stage', 'ITEM', cardinality=One ,show=True)
    annotation = RelationshipTo('Annotation', 'IS_ANNOTATED_BY')

## Annotation data model

#class Annotation(IdentifiedNode):
#    key = StringProperty(required=True)
#    value = StringProperty(required=True)
#    video = RelationshipFrom('Video', 'IS_ANNOTATED_BY')

class Annotation(IdentifiedNode):
    """Annotation class"""
    ANNOTATION_TYPES = (
        ('OD', 'object detection'),
        ('OR', 'object recognition'),
        ('VQ', 'video quality'),
        ('TVS', 'temporal video segmentation')
    )
    AUTOMATIC_GENERATOR_TOOLS = (
        ('FHG', 'Fraunhofer tool'),
        ('VIS', 'Google Vision API'),
        ('AWS', 'Amazon Rekognition API')
    )
    type = StringProperty(required=True, choices=ANNOTATION_TYPES)
    creation_datetime = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    source = RelationshipFrom('Video', 'IS_ANNOTATED_BY')
    creator = RelationshipTo(
        'User', 'IS_CREATED_BY', cardinality=ZeroOrOne)
    generator = StringProperty(choices=AUTOMATIC_GENERATOR_TOOLS)
    bodies = RelationshipTo('AnnotationBody', 'HAS_BODY', cardinality=ZeroOrMore)
    targets = RelationshipTo('AnnotationTarget', 'HAS_TARGET', cardinality=OneOrMore)

class AnnotationBody(StructuredNode):
    __abstract_node__ = True

class TextBody(AnnotationBody):
    # TODO
    pass

class ImageBody(AnnotationBody):
    # TODO
    pass

class AudioBody(AnnotationBody):
    # TODO
    pass

class VQBody(AnnotationBody):
    """Class for Video Quality Annotation"""
    module = StringProperty(required=True)
    frames = RelationshipTo('VQFrame', 'FRAME', cardinality=OneOrMore)

class VQFrame(StructuredNode):
    idx = IntegerProperty(required=True)
    quality = FloatProperty(required=True)

class TVSBody(AnnotationBody):
    shots = RelationshipTo('Shot', 'SHOT', cardinality=OneOrMore)

class Shot(StructuredNode):
    """Shot class"""
    start_frame_idx = IntegerProperty()
    end_frame_idx = IntegerProperty()
    duration = IntegerProperty()

class ODBody(StructuredNode):
    """Object Detection"""
    #OBJECT_TYPES = ('FACE', 'LEFT_EYE', 'RIGHT_EYE')
    object_id = StringProperty(required=True)
    object_type = StringProperty(required=True)
    # FIXME add object attribute relationship
    #object_attributes = RelationshipTo('ObjectAttribute', 'HAS_ATTRIBUTE', cardinality=ZeroOrMore)


class TargetBody(StructuredNode):
    __abstract_node__ = True

