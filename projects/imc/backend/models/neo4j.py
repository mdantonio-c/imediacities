# -*- coding: utf-8 -*-

"""
Graph DB abstraction from neo4j server.
These are custom models!

VERY IMPORTANT!
Imports and models have to be defined/used AFTER normal Graphdb connection.
"""

import sys
from datetime import datetime
import pytz

from rapydo.services.neo4j.models import (
    StringProperty, ArrayProperty, IntegerProperty,
    FloatProperty, DateTimeProperty, DateProperty,
    StructuredNode, StructuredRel, IdentifiedNode,
    TimestampedNode, RelationshipTo, RelationshipFrom,
)
from neomodel import ZeroOrMore, OneOrMore, ZeroOrOne, One

from rapydo.models.neo4j import User as UserBase
from imc.models import codelists

import logging

log = logging.getLogger(__name__)


class HeritableStructuredNode(StructuredNode):

    # noqa see: http://stackoverflow.com/questions/35744456/relationship-to-multiple-types-polymorphism-in-neomodel

    """
    Useful to manage polymorphic relationships providing downcasting.

    Extends :class:`neomodel.StructuredNode` to provide the :meth:`.downcast`
    method.
    """

    __abstract_node__ = True

    def downcast(self, target_class=None):
        """
        Re-instantiate this node as an instance its most derived derived class.
        """
        # TODO: there is probably a far more robust way to do this.
        _get_class = lambda cname: getattr(sys.modules[__name__], cname)

        # inherited_labels() only returns the labels for the current class and
        #  any super-classes, whereas labels() will return all labels on the
        #  node.
        classes = list(set(self.labels()) - set(self.inherited_labels()))

        if len(classes) == 0:
            # The most derivative class is already instantiated.
            return self
        cls = None

        if target_class is None:    # Caller has not specified the target.
            if len(classes) == 1:    # Only one option, so this must be it.
                target_class = classes[0]
            else:
                # Infer the most derivative class by looking for the one
                # with the longest method resolution order.
                class_objs = map(_get_class, classes)
                _, cls = sorted(
                    zip(
                        map(lambda cls: len(cls.mro()), class_objs),
                        class_objs),
                    key=lambda size, cls: size)[-1]
        else:    # Caller has specified a target class.
            if not isinstance(target_class, str):
                # In the spirit of neomodel, we might as well support both
                #  class (type) objects and class names as targets.
                target_class = target_class.__name__

            if target_class not in classes:
                raise ValueError('%s is not a sub-class of %s'
                                 % (target_class, self.__class__.__name__))
        if cls is None:
            cls = getattr(sys.modules[__name__], target_class)
        instance = cls.inflate(self.id)

        # TODO: Can we re-instatiate without hitting the database again?
        instance.refresh()
        return instance

##############################################################################
# MODELS
##############################################################################

# Extension of User model for accounting in API login/logout


class User(UserBase):
    # name_surname = StringProperty(required=True, unique_index=True)

    items = RelationshipFrom('Item', 'IS_OWNED_BY', cardinality=ZeroOrMore)
    annotations = RelationshipFrom(
        'Annotation', 'IS_ANNOTATED_BY', cardinality=ZeroOrMore)
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
    item = RelationshipFrom('Item', 'CONTENT_SOURCE', cardinality=ZeroOrOne)

# CREATION: descriptive data model
##############################################################################


class AnnotationTarget(HeritableStructuredNode):
    # __abstract_node__ = True
    # __label__ = 'Item'
    annotation = RelationshipFrom('Annotation', 'HAS_TARGET', cardinality=One)


class Item(TimestampedNode, AnnotationTarget):
    """
    The Item Entity points to the digital file held in the IMC repository.
    The item functions as a logical wrapper for the digital object displayed in
    IMC.

    Attributes:
        is_shown_by     An unambiguous URL reference to the digital object in
                        the IMC repository.
        is_shown_at     An unambiguous URL reference to the digital object on
                        the IMC web site and/or on the content provider's web
                        site in its full information context.
        thumbnail       Link to the reduced-size image of the AV or NonAV
                        digital object.
        summary         Link to the summary image of the AV digital object (not
                        available for NonAV digital object)
        duration        The running time of the digitised audiovisual
                        manifestation measured in minutes and seconds.
        framerate       Optional value for the projection speed, given in
                        frames per second, to which the given duration refers.
        dimension       The total physical dimension of the digital object
                        (i.e. file size in bytes) represented as numeric value,
                        with decimal places if required.
        dimension_unit  Unit of the physical dimension of the item: "bytes"
        digital_format  The description of the digital file in which a content
                        object is stored. Array[0]=container; Array[1]=coding;
                        Array[2]=format; Array[3]=resolution:
                        - container: e.g."AVI", "MP4", "3GP", "RealMedia"
                        - coding: e.g. "WMA","WMV", "MPEG-4", "RealVideo"
                        - format: RFC 2049 MIME types, e.g. "image/jpg", etc.
                        - resolution: The degree of sharpness of the digital
                                     object expressed in lines or pixel
        uri             An unambiguous URI to the resource within the IMC
                        context.
        item_type       "Text", "Image" or "Video"
        license         A reference to the license that applies to the digital
                        item.
    """
    thumbnail = StringProperty()
    summary = StringProperty()
    duration = FloatProperty(show=True)
    framerate = StringProperty(show=True)  # FloatProperty()
    digital_format = ArrayProperty(StringProperty(), required=False, show=True)
    uri = StringProperty()
    item_type = StringProperty(required=True, show=True)
    # TODO add license reference
    ownership = RelationshipTo(
        'Group', 'IS_OWNED_BY', cardinality=ZeroOrMore, show=True)
    content_source = RelationshipTo(
        'Stage', 'CONTENT_SOURCE', cardinality=One)
    meta_source = RelationshipTo(
        'Stage', 'META_SOURCE', cardinality=One)
    creation = RelationshipTo(
        'Creation', 'CREATION', cardinality=ZeroOrOne)
    sourcing_annotations = RelationshipFrom(
        'Annotation', 'SOURCE', cardinality=ZeroOrMore)
    targeting_annotations = RelationshipFrom(
        'Annotation', 'HAS_TARGET', cardinality=ZeroOrMore)
    shots = RelationshipTo(
        'Shot', 'SHOT', cardinality=ZeroOrMore)


class ContributionRel(StructuredRel):
    """
    Attributes:
        activities  One or more film-related activities of the person taken
                    from relationship records or from secondary sources.
    """
    activities = ArrayProperty(StringProperty(), show=True)


class Creation(IdentifiedNode, HeritableStructuredNode):
    """
    It stores descriptive metadata on IMC objects provided by the archives with
    the initial ingest.
    It is an abstraction for both 'audiovisual' and 'non audiovisual' works.

    Attributes:
        identifiers:        TODO
        record_sources      List of sources from which the record comes.
        titles              List of titles. Titles can be a word, phrase or
                            character, naming the work or a group of works, a
                            particular manifestation or an individual item.
        keywords            Set of vocabulary terms describing the content of a
                            creation.
        descriptions        Textual descriptions.
        languages           The languages of the spoken, sung or written
                            content.
        coverages           The spatial or temporal topics of the creation
                            object.
        provenance          Organisation which owns or has custody of the item.
        rights_status       Specifies the copyright status of the digital item.
        rightholders        Right holders.
        collection_title    A textual title of the archival collection of which
                            the creation is part.
        contributors        Agents which are involved in the creation of the
                            objects.
    """
    record_sources = RelationshipTo(
        'RecordSource', 'RECORD_SOURCE', cardinality=OneOrMore, show=True)
    titles = RelationshipTo(
        'Title', 'HAS_TITLE', cardinality=OneOrMore, show=True)
    keywords = RelationshipTo(
        'Keyword', 'HAS_KEYWORD', cardinality=ZeroOrMore, show=True)
    descriptions = RelationshipTo(
        'Description', 'HAS_DESCRIPTION', cardinality=OneOrMore, show=True)
    languages = RelationshipTo(
        'CreationLanguage', 'HAS_LANGUAGE', cardinality=ZeroOrMore, show=True)
    coverages = RelationshipTo(
        'Coverage', 'HAS_COVERAGE', cardinality=ZeroOrMore, show=True)
    # provenance = RelationshipTo(
    #    'Group', 'HAS_PROVENENCE', cardinality=ZeroOrOne, show=True)
    rights_status = StringProperty(show=True)
    # FIXME: 1..N from specifications???
    rightholders = RelationshipTo(
        'Rightholder', 'COPYRIGHTED_BY', cardinality=ZeroOrMore, show=True)
    collection_title = StringProperty(show=True)
    contributors = RelationshipTo(
        'Agent', 'CONTRIBUTED_BY', cardinality=ZeroOrMore, show=True,
        model=ContributionRel)
    item = RelationshipFrom(
        'Item', 'CREATION', cardinality=One, show=True)


class Title(StructuredNode):
    """Wrapper class for title.

    Attributes:
        text                The textual expression of the title.
        language            The language of the title.
        part_designations   TODO
        relationship        The type of relationship between the title and the
                            entity to which it is assigned (e.g. "Original
                            title", "Distribution title", "Translated title"
                            etc).
    """
    text = StringProperty(required=True, show=True)
    language = StringProperty(choices=codelists.LANGUAGE, show=True)
    relationship = StringProperty(
        required=True, choices=codelists.TITLE_RELASHIONSHIPS, show=True)
    creation = RelationshipFrom(
        'Creation', 'HAS_TITLE', cardinality=One, show=True)


class Keyword(StructuredNode):
    """
    A term or set of vocabulary terms describing the content of a creation.
    This can be keywords or other vocabularies to describe subjects. Controlled
    and uncontrolled terms can be used together, but not within a single set of
    terms. Likewise, if more than one controlled vocabulary is used, then terms
    from each of these must be contained in a separate instance of this
    element. A separate instance is also required for each language if terms in
    more than one language are taken from a multilingual vocabulary.

    Attributes:
        term            The term value. This can be the textual value of the
                        term. For non-textual terms the classification codes,
                        preferably a combination of the code and the verbal
                        class description should be indicated.
        termID          A non-text identifier that can be combined with the
                        scheme ID from a unique resource identifier for the
                        term within a controlled vocabulary.
        keyword_type    Type of information described by the keywords.
        language        The language of the content of each subject.
        scheme          A unique identifier denoting the controlled vocabulary
                        (preferably URI). If the subject terms are not from a
                        controlled vocabulary, the value of this element should
                        be set to "uncontrolled".
    """
    term = StringProperty(index=True, required=True, show=True)
    termID = IntegerProperty(show=True)
    keyword_type = StringProperty(choices=codelists.KEYWORD_TYPES, show=True)
    language = StringProperty(choices=codelists.LANGUAGE, show=True)
    creation = RelationshipFrom(
        'Creation', 'HAS_KEYWORD', cardinality=One, show=True)


class Description(StructuredNode):
    """
    Wrapper for the description of a creation.

    Attributes:
        text              Textual descriptions include synopses, plot
                          summaries, reviews, transcripts or shot lists.
                          They can occur in more than one language and they can
                          have statements of authorship or references to
                          external resources.
        language          The language of the description text.
        description_type  A keyword denoting the type of description.
        source_ref        Either the name of the institution, or an URI
                          identifying the source directly or via a reference
                          system such as an on-line catalogue.
    """
    text = StringProperty(index=True, required=True, show=True)
    language = StringProperty(choices=codelists.LANGUAGE, show=True)
    description_type = StringProperty(
        choices=codelists.DESCRIPTION_TYPES, show=True)
    source_ref = StringProperty()
    creation = RelationshipFrom(
        'Creation', 'HAS_DESCRIPTION', cardinality=One, show=True)


class CreationLanguage(StructuredNode):
    """
    The language of the spoken, sung or written content.

    Attributes:
        value   The language code.
        usage   This indicates the relationship between the language and the
                creation.
    """
    value = StringProperty(
        choices=codelists.LANGUAGE, show=True, required=True)
    usage = StringProperty(choices=codelists.LANGUAGE_USAGES)
    creation = RelationshipFrom(
        'Creation', 'HAS_LANGUAGE', cardinality=One, show=True)


class Coverage(StructuredNode):
    """
    The spatial or temporal topic of the creation object.

    Attributes:
        spatial     This may be a named place, a location, a spatial
                    coordinate, a named administrative entity or an URI to a
                    LOD-service.
        temporal    This may be a period, date or range date.
    """
    spatial = ArrayProperty(StringProperty(), required=True, show=True)
    temporal = ArrayProperty(StringProperty(), show=True)
    creation = RelationshipFrom(
        'Creation', 'HAS_COVERAGE', cardinality=One, show=True)


class Rightholder(IdentifiedNode):
    """ Rightholder.

    Attributes:
        name    Name of the copyright holder.
        url     If available, URL to the homepage of the copyright holder.
    """
    name = StringProperty(index=True, required=True, show=True),
    url = StringProperty()
    creation = RelationshipFrom(
        'Creation', 'COPYRIGHTED_BY', cardinality=One, show=True)


class Agent(IdentifiedNode):
    """
    It refers mostly to agents which are involved in the creation of the
    objects.

    Attributes:
        record_sources      List of sources from which the record comes.
        agent_type          Defines the type of the Agent (person, corporate
                            body, family etc.).
        names               Name(s) by which the entity is (or was) known.
        birth_date          Date of birth ("“"CCYY-MM-DD" or "CCYY").
        death_date          Date of death ("CCYY-MM-DD" or "CCYY").
        biographical_note   Short biographical note about a person or
                            organisation.
        biography_views     Unambiguous URL references to a full biographical
                            entry in an external database or on content
                            provider's website.
    """
    # any other identifiers?
    # (from different schemes different from the internal uuid)
    # identifiers = RelationshipTo(
    #     'Identifier', 'IS_IDENTIFIED_BY', cardinality=OneOrMore, show=True)
    record_sources = RelationshipTo(
        'RecordSource', 'RECORD_SOURCE', cardinality=OneOrMore, show=True)
    agent_type = StringProperty(required=True, choices=codelists.AGENT_TYPES)
    names = ArrayProperty(StringProperty(), required=True)
    birth_date = DateProperty(show=True)
    death_date = DateProperty(default=None, show=True)
    biographical_note = StringProperty()
    sex = StringProperty(choices=codelists.SEXES, show=True)
    biography_views = ArrayProperty(StringProperty(), required=False)
    creation = RelationshipFrom(
        'Creation', 'CONTRIBUTED_BY', cardinality=ZeroOrMore, show=True)


# class Identifier(StructuredNode):
#     """
#     Identifier generated by the system (GUID or ID chosen from an external
#     naming schema).
#     """
#     IDENTIFIER_SCHEME = (
#         ('UUID', '')
#     )
#     scheme = StringProperty(required=True, choices=IDENTIFIER_SCHEME)
#     value = StringProperty(required=True)


class RecordSource(StructuredNode):
    """ A reference to the IMC content provider and their local ID.

    Attributes:
        source_id        The local identifier of the record. If this does not
                        exist in the content provider´s database the value is
                        "undefined".
        provider_name   The name of the archive supplying the record.
        provider_id      An unambiguous reference to the archive supplying the
                        record.
        provider_scheme Name of the registration scheme encoding the
                        institution name ("ISIL code" or "Institution acronym")
        is_shown_at     An unambiguous URL reference to the digital object on
                        the web site of the source provider and/or on the
                        content provider's web site in its full information
                        context.
    """
    source_id = StringProperty(required=True, show=True)
    provider_name = StringProperty(index=True, required=True, show=True)
    provider_id = StringProperty(required=True, show=True)
    provider_scheme = StringProperty(
        choices=codelists.PROVIDER_SCHEMES, required=True, show=True)
    is_shown_at = StringProperty(show=True)
    creation = RelationshipFrom(
        'Creation', 'RECORD_SOURCE', cardinality=OneOrMore, show=True)


class AVEntity(Creation):
    """
    The AVEntity is designed to store descripticve metadata on IMC audiovisual
    objects provided by the archives with the initial ingest.
    This entity extends Creation class that wraps common metadata.

    Attributes:
        identifying_title           A short phrase for identifying the
                                    audiovisual creation, to be used e.g. in
                                    human-readable result lists from database
                                    queries.
        identifying_title_origin    Acronym or other identifier indicating the
                                    origin of the element content.
        production_countries        The geographic origin of an audiovisual
                                    creation. This should be the country or
                                    countries where the production facilities
                                    are located.
        production_years            The year or time span associated with the
                                    production of the audiovisual creation
                                    (e.g. CCYY, CCYY-CCYY).
        video_format                The description of the physical artefact or
                                    digital file on which an audiovisual
                                    manifestation is fixed.
        view_filmography            An unambiguous URL reference to the full
                                    filmographic entry of a film on the content
                                    provider web site.
    """
    identifying_title = StringProperty(index=True, required=True, show=True)
    identifying_title_origin = StringProperty(index=True, show=True)
    production_countries = ArrayProperty(StringProperty(), show=True)
    production_years = ArrayProperty(
        StringProperty(), required=True, show=True)
    video_format = RelationshipTo(
        'VideoFormat', 'VIDEO_FORMAT', cardinality=ZeroOrOne, show=True)
    view_filmography = StringProperty(show=True)


class VideoFormat(StructuredNode):
    """
    The description of the physical artefact or digital file on which an
    audiovisual manifestation is fixed.

    Attributes:
        gauge           The width of the film stock or other carrier (such as
                        magnetic tape) used for the manifestation.
        aspect_ratio    The ratio between width and height of the image (e.g.
                        "full frame", "cinemascope", "1:1,33").
        sound           Element from values list.
        colour          Element from values list.
    """
    gauge = StringProperty(show=True)
    aspect_ratio = StringProperty(show=True)
    sound = StringProperty(choices=codelists.VIDEO_SOUND, show=True)
    colour = StringProperty(show=True)
    creation = RelationshipFrom(
        'AVEntity', 'FROM_AV_ENTITY', cardinality=OneOrMore, show=True)


class NonAVEntity(Creation):
    """
    Non-audiovisual objects in IMC can be pictures, photos, correspondence,
    books, periodicals etc.

    Attributes:
        date_created            The point or period of time associated with the
                                creation of the non-audiovisual creation
                                (“CCYY-MM-DD”, “CCYY”, CCYY-CCYY). If the
                                production year is unknown, the term “unknown”
                                should be added to indicate that research
                                regarding the production time has been
                                unsuccessful.
        non_av_entity_type      The general type of the non-audiovisual
                                manifestation (“image” or “text”).
        specific_type           This element further specifies the type of the
                                non-audiovisual entity.
        phisical_format_size    The dimensions of the physical object.
        colour                  This element can be used to indicate the colour
                                of a non-audiovisual object (e.g. "black and
                                white", "colour", "mixed").
    """
    date_created = ArrayProperty(StringProperty(), required=True, show=True)
    non_av_entity_type = StringProperty(required=True,
                                        choices=codelists.NON_AV_ENTITY_TYPES,
                                        show=True)
    specific_type = StringProperty(
        required=True, choices=codelists.NON_AV_ENTITY_SPECIFIC_TYPES,
        show=True)
    phisical_format_size = StringProperty(show=True)
    colour = StringProperty(choices=codelists.COLOUR, show=True)

# ANNOTATION
##############################################################################

# class Annotation(IdentifiedNode):
#    key = StringProperty(required=True)
#    value = StringProperty(required=True)
#    video = RelationshipFrom('Video', 'IS_ANNOTATED_BY')


class AnnotationCreatorRel(StructuredRel):
    when = DateTimeProperty(default=lambda: datetime.now(pytz.utc))


class Annotation(IdentifiedNode):
    """Annotation class"""
    ANNOTATION_TYPES = (
        ('OD', 'object detection'),
        ('OR', 'object recognition'),
        ('VQ', 'video quality'),
        ('VIM', 'video image motion'),
        ('TVS', 'temporal video segmentation')
    )
    AUTOMATIC_GENERATOR_TOOLS = (
        ('FHG', 'Fraunhofer tool'),
        ('VIS', 'Google Vision API'),
        ('AWS', 'Amazon Rekognition API')
    )
    annotation_type = StringProperty(
        required=True, choices=ANNOTATION_TYPES, show=True)
    creation_datetime = DateTimeProperty(
        default=lambda: datetime.now(pytz.utc), show=True)
    source_item = RelationshipTo('Item', 'SOURCE', cardinality=One, show=True)
    creator = RelationshipTo(
        'User', 'IS_ANNOTATED_BY', cardinality=ZeroOrOne,
        model=AnnotationCreatorRel, show=True)
    generator = StringProperty(choices=AUTOMATIC_GENERATOR_TOOLS, show=True)
    bodies = RelationshipTo(
        'AnnotationBody', 'HAS_BODY', cardinality=ZeroOrMore)
    targets = RelationshipTo(
        'AnnotationTarget', 'HAS_TARGET', cardinality=OneOrMore, show=True)


class AnnotationBody(HeritableStructuredNode):
    annotation = RelationshipFrom('Annotation', 'HAS_BODY', cardinality=One)


class TextBody(AnnotationBody):
    # TODO
    pass


class ImageBody(AnnotationBody):
    # TODO
    pass


class AudioBody(AnnotationBody):
    audio_format = StringProperty(show=True)
    language = StringProperty(show=True)
    # TODO


# class VQBody(AnnotationBody):
#     """Class for Video Quality Annotation."""
#     module = StringProperty(required=True)
#     frames = RelationshipTo('VQFrame', 'FRAME', cardinality=OneOrMore)


class VIMBody(AnnotationBody):
    """
    Class for Video Quality Annotation.

    [avg value, max value]
    """
    no_motion = ArrayProperty(FloatProperty(), show=True)
    left_motion = ArrayProperty(FloatProperty(), show=True)
    right_motion = ArrayProperty(FloatProperty(), show=True)
    up_motion = ArrayProperty(FloatProperty(), show=True)
    down_motion = ArrayProperty(FloatProperty(), show=True)
    zoom_in_motion = ArrayProperty(FloatProperty(), show=True)
    zoom_out_motion = ArrayProperty(FloatProperty(), show=True)
    roll_cw_motion = ArrayProperty(FloatProperty(), show=True)
    roll_ccw_motion = ArrayProperty(FloatProperty(), show=True)
    x_shake = ArrayProperty(FloatProperty(), show=True)
    y_shake = ArrayProperty(FloatProperty(), show=True)
    roll_shake = ArrayProperty(FloatProperty(), show=True)
    camera_shake = ArrayProperty(FloatProperty(), show=True)
    inner_rhythm_fluid = ArrayProperty(FloatProperty(), show=True)
    inner_rhythm_staccato = ArrayProperty(FloatProperty(), show=True)
    inner_rhythm_no_motion = ArrayProperty(FloatProperty(), show=True)


# class VQFrame(StructuredNode):
#     idx = IntegerProperty(required=True)
#     quality = FloatProperty(required=True)


class TVSBody(AnnotationBody):
    segments = RelationshipTo(
        'Shot', 'SEGMENT', cardinality=OneOrMore, show=True)


class Shot(IdentifiedNode, AnnotationTarget):
    """Shot class"""
    shot_num = IntegerProperty(required=True, show=True)
    start_frame_idx = IntegerProperty(required=True, show=True)
    end_frame_idx = IntegerProperty(show=True)
    frame_uri = StringProperty()
    thumbnail_uri = StringProperty()
    timestamp = StringProperty(show=True)
    duration = FloatProperty(show=True)
    annotation_body = RelationshipFrom(
        'Annotation', 'SEGMENT', cardinality=One)
    item = RelationshipFrom('Item', 'SHOT', cardinality=One)


class ODBody(StructuredNode):
    """Object Detection"""
    # OBJECT_TYPES = ('FACE', 'LEFT_EYE', 'RIGHT_EYE')
    object_id = StringProperty(required=True)
    object_type = StringProperty(required=True)
    # FIXME add object attribute relationship
    # object_attributes = RelationshipTo(
    #              'ObjectAttribute', 'HAS_ATTRIBUTE', cardinality=ZeroOrMore)