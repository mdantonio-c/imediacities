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

from restapi.services.neo4j.models import (
    StringProperty, ArrayProperty, IntegerProperty, BooleanProperty,
    FloatProperty, DateTimeProperty, DateProperty, JSONProperty, EmailProperty,
    StructuredNode, StructuredRel, IdentifiedNode,
    TimestampedNode, RelationshipTo, RelationshipFrom,
)
from neomodel import ZeroOrMore, OneOrMore, ZeroOrOne, One

from restapi.models.neo4j import User as UserBase
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
        def _get_class(cname): return getattr(sys.modules[__name__], cname)

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
                    key=lambda size_cls: size_cls[0])[-1]
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


class RevisionRel(StructuredRel):
    """
    Attributes:
        when  Date of start or approval of a revision.
    """
    when = DateTimeProperty(
        default=lambda: datetime.now(pytz.utc, show=True)
    )


class User(UserBase):
    # name_surname = StringProperty(required=True, unique_index=True)

    items = RelationshipFrom('Item', 'IS_OWNED_BY', cardinality=ZeroOrMore)
    annotations = RelationshipFrom(
        'Annotation', 'IS_ANNOTATED_BY', cardinality=ZeroOrMore)
    belongs_to = RelationshipTo('Group', 'BELONGS_TO', show=True)
    coordinator = RelationshipTo(
        'Group', 'PI_FOR', cardinality=ZeroOrMore, show=True)
    items_under_revision = RelationshipFrom(
        'Item', 'REVISION_BY', cardinality=ZeroOrMore)
    revised_shots = RelationshipFrom(
        'Shot', 'REVISED_BY', cardinality=ZeroOrMore)


class Group(IdentifiedNode):
    fullname = StringProperty(required=True, unique_index=True, show=True)
    shortname = StringProperty(required=True, unique_index=True, show=True)

    members = RelationshipFrom(
        'User', 'BELONGS_TO', cardinality=ZeroOrMore, show=True)
    coordinator = RelationshipFrom(
        'User', 'PI_FOR', cardinality=ZeroOrMore, show=True)
    stage_files = RelationshipFrom(
        'Stage', 'IS_OWNED_BY', cardinality=ZeroOrMore, show=False)


class Stage(TimestampedNode, HeritableStructuredNode):
    # __abstract_node__ = True
    filename = StringProperty(required=True, show=True)
    path = StringProperty(required=True, unique_index=True, show=True)
    status = StringProperty(show=True)
    status_message = StringProperty(show=True)
    warnings = ArrayProperty(StringProperty(), show=True)
    task_id = StringProperty(show=True)
    ownership = RelationshipTo(
        'Group', 'IS_OWNED_BY', cardinality=ZeroOrMore, show=True)


class MetaStage(Stage):
    item = RelationshipFrom('Item', 'META_SOURCE', cardinality=ZeroOrOne)


class ContentStage(Stage):
    item = RelationshipFrom('Item', 'CONTENT_SOURCE', cardinality=ZeroOrOne)


# CREATION: descriptive data model
##############################################################################


class AnnotationTarget(HeritableStructuredNode):
    annotation = RelationshipFrom(
        'Annotation', 'HAS_TARGET', cardinality=ZeroOrMore)


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
                        (i.e. file size in bytes) represented as numeric value.
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
    dimension = IntegerProperty(show=True)
    framerate = StringProperty(show=True)
    digital_format = ArrayProperty(StringProperty(), required=False, show=True)
    uri = StringProperty()
    item_type = StringProperty(
        required=True, choices=codelists.CONTENT_TYPES, show=True)
    ownership = RelationshipTo(
        'Group', 'IS_OWNED_BY', cardinality=One, show=True)
    content_source = RelationshipTo(
        'ContentStage', 'CONTENT_SOURCE', cardinality=ZeroOrOne)
    meta_source = RelationshipTo(
        'MetaStage', 'META_SOURCE', cardinality=One)
    creation = RelationshipTo(
        'Creation', 'CREATION', cardinality=ZeroOrOne)
    sourcing_annotations = RelationshipFrom(
        'Annotation', 'SOURCE', cardinality=ZeroOrMore)
    targeting_annotations = RelationshipFrom(
        'Annotation', 'HAS_TARGET', cardinality=ZeroOrMore)
    shots = RelationshipTo(
        'Shot', 'SHOT', cardinality=ZeroOrMore)
    revision = RelationshipTo(
        'User', 'REVISION_BY', cardinality=ZeroOrOne, model=RevisionRel)


class ContributionRel(StructuredRel):
    """
    Attributes:
        activities  One or more film-related activities of the person taken
                    from relationship records or from secondary sources.
    """
    activities = ArrayProperty(StringProperty(), show=True)


class LanguageRel(StructuredRel):
    """This indicates the usage relationship between the language and the
       creation."""
    usage = StringProperty(choices=codelists.LANGUAGE_USAGES, show=True)


class Creation(IdentifiedNode, HeritableStructuredNode):
    """
    It stores descriptive metadata on IMC objects provided by the archives with
    the initial ingest.
    It is an abstraction for both 'audiovisual' and 'non audiovisual' works.

    Attributes:
        external_ids:       IDs chosen from external schemas.
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
        rights_status       Specifies the copyright status of the digital item.
        rightholders        Right holders.
        collection_title    A textual title of the archival collection of which
                            the creation is part.
        contributors        Agents which are involved in the creation of the
                            objects.
    """
    external_ids = ArrayProperty(StringProperty(), show=True)
    record_sources = RelationshipTo(
        'RecordSource', 'RECORD_SOURCE', cardinality=OneOrMore, show=True)
    titles = RelationshipTo(
        'Title', 'HAS_TITLE', cardinality=OneOrMore, show=True)
    keywords = RelationshipTo(
        'Keyword', 'HAS_KEYWORD', cardinality=ZeroOrMore, show=True)
    descriptions = RelationshipTo(
        'Description', 'HAS_DESCRIPTION', cardinality=OneOrMore, show=True)
    languages = RelationshipTo(
        'Language', 'HAS_LANGUAGE', cardinality=ZeroOrMore, model=LanguageRel,
        show=True)
    coverages = RelationshipTo(
        'Coverage', 'HAS_COVERAGE', cardinality=ZeroOrMore, show=True)
    rights_status = StringProperty(
        choices=codelists.RIGHTS_STATUS, required=True, show=True)
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
        part_designations   A combination of the name of a structuring unit and
                            the count value that identifies the current entity
                            as an individual part of a complex work.
        relation            The type of relationship between the title and the
                            entity to which it is assigned (e.g. "Original
                            title", "Distribution title", "Translated title"
                            etc).
    """
    text = StringProperty(required=True, show=True)
    language = StringProperty(choices=codelists.LANGUAGE, show=True)
    part_designations = ArrayProperty(StringProperty(), show=True)
    relation = StringProperty(choices=codelists.AV_TITLE_TYPES, show=True)
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
        schemeID        A unique identifier denoting the controlled vocabulary
                        (preferably URI). If the subject terms are not from a
                        controlled vocabulary, the value of this element should
                        be set to "uncontrolled".
    """
    term = StringProperty(index=True, required=True, show=True)
    termID = IntegerProperty(show=True)
    keyword_type = StringProperty(choices=codelists.KEYWORD_TYPES, show=True)
    language = StringProperty(choices=codelists.LANGUAGE, show=True)
    schemeID = StringProperty(show=True)
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
    source_ref = StringProperty(show=True)
    creation = RelationshipFrom(
        'Creation', 'HAS_DESCRIPTION', cardinality=One, show=True)


class Language(StructuredNode):
    """
    ISO-639-1 LanguageCS

    Attributes:
        code   The language code.
        labels The translation into different languages.
    """
    code = StringProperty(
        choices=codelists.LANGUAGE, show=True, required=True)
    creation = RelationshipFrom(
        'Creation', 'HAS_LANGUAGE', cardinality=ZeroOrMore)


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
    name = StringProperty(required=True, show=True)
    url = StringProperty(show=True)
    creation = RelationshipFrom(
        'Creation', 'COPYRIGHTED_BY', cardinality=ZeroOrMore)


class Agent(IdentifiedNode):
    """
    It refers mostly to agents which are involved in the creation of the
    objects.

    Attributes:
        uuid                Identifier generated by the system.
        external_ids        IDs chosen from external schemas.
        record_sources      List of sources from which the record comes.
        agent_type          Defines the type of the Agent (person, corporate
                            body, family etc.).
        names               Name(s) by which the entity is (or was) known.
        birth_date          Date of birth ("CCYY-MM-DD" or "CCYY").
        death_date          Date of death ("CCYY-MM-DD" or "CCYY").
        biographical_note   Short biographical note about a person or
                            organisation.
        biography_views     Unambiguous URL references to a full biographical
                            entry in an external database or on content
                            provider's website.
    """
    # record_sources = RelationshipTo(
    #     'RecordSource', 'RECORD_SOURCE', cardinality=OneOrMore, show=True)
    external_ids = ArrayProperty(StringProperty(), show=True)
    agent_type = StringProperty(
        required=True, choices=codelists.AGENT_TYPES, show=True)
    names = ArrayProperty(StringProperty(), required=True, show=True)
    birth_date = DateProperty(show=True)
    death_date = DateProperty(default=None, show=True)
    biographical_note = StringProperty()
    sex = StringProperty(choices=codelists.SEXES, show=True)
    biography_views = ArrayProperty(StringProperty())
    creation = RelationshipFrom(
        'Creation', 'CONTRIBUTED_BY', cardinality=ZeroOrMore, show=True)


class RecordSource(StructuredNode):
    """ A reference to the IMC content provider and their local ID.

    Attributes:
        source_id       The local identifier of the record. If this does not
                        exist in the content provider´s database the value is
                        "undefined".
        is_shown_at     An unambiguous URL reference to the digital object on
                        the web site of the source provider and/or on the
                        content provider's web site in its full information
                        context.
    """
    source_id = StringProperty(required=True, show=True)
    is_shown_at = StringProperty(show=True)
    provider = RelationshipTo(
        'Provider', 'PROVIDED_BY', cardinality=One, show=True)
    creation = RelationshipFrom(
        'Creation', 'RECORD_SOURCE', cardinality=One)


class Provider(IdentifiedNode):
    """
    name         The name of the archive supplying the record.
    identifier   An unambiguous reference to the archive supplying the record.
    scheme       Name of the registration scheme encoding the institution name
                 ("ISIL code" or "Institution acronym")
    address      The address of the archive
    phone        The phone number of the archive
    fax          The fax number of the archive
    website      The website of the archive
    email        The email of the archive
    """
    name = StringProperty(index=True, required=True, show=True)
    identifier = StringProperty(required=True, show=True)
    scheme = StringProperty(
        choices=codelists.PROVIDER_SCHEMES, required=True, show=True)
    address = StringProperty(required=False, show=True)
    phone = StringProperty(required=False, show=True)
    fax = StringProperty(required=False, show=True)
    website = StringProperty(required=False, show=True)
    email = EmailProperty(required=False, show=True)
    record_source = RelationshipFrom(
        'RecordSource', 'RECORD_SOURCE', cardinality=ZeroOrMore)


class CountryOfReferenceRel(StructuredRel):
    """
    The relationship between a geographic area and the audiovisual creation.
    Defaults to "production".
    """
    reference = StringProperty(default="Country of Production", show=True)


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
        production_years            The year or time span associated with the
                                    production of the audiovisual creation
                                    (e.g. CCYY, CCYY-CCYY).
        production_countries        The geographic origin of an audiovisual
                                    creation. This should be the country or
                                    countries where the production facilities
                                    are located.
        video_format                The description of the physical artefact or
                                    digital file on which an audiovisual
                                    manifestation is fixed.
        view_filmography            An unambiguous URL reference to the full
                                    filmographic entry of a film on the content
                                    provider web site.
    """
    identifying_title = StringProperty(index=True, required=True, show=True)
    identifying_title_origin = StringProperty(index=True, show=True)
    production_years = ArrayProperty(
        StringProperty(), required=True, show=True)
    production_countries = RelationshipTo(
        'Country', 'COUNTRY_OF_REFERENCE', cardinality=ZeroOrMore,
        model=CountryOfReferenceRel, show=True)
    video_format = RelationshipTo(
        'VideoFormat', 'VIDEO_FORMAT', cardinality=ZeroOrOne, show=True)
    view_filmography = ArrayProperty(StringProperty(), show=True)


class Country(StructuredNode):
    """
    ISO 3166-1,
    ISO 3166-2 (Region codes),
    ISO 3166-3,
    AFNOR XP2 44-002

    Attributes:
        code   The country code.
        labels The translation into different languages.
    """
    code = StringProperty(choices=codelists.COUNTRY, show=True, required=True)
    creation = RelationshipFrom(
        'AVEntity', 'COUNTRY_OF_REFERENCE', cardinality=ZeroOrMore)


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
    gauge = StringProperty(choices=codelists.GAUGE, show=True)
    aspect_ratio = StringProperty(choices=codelists.ASPECT_RATIO, show=True)
    sound = StringProperty(choices=codelists.VIDEO_SOUND, show=True)
    colour = StringProperty(choices=codelists.COLOUR, show=True)
    creation = RelationshipFrom(
        'AVEntity', 'VIDEO_FORMAT', cardinality=One, show=True)

    def __str__(self):
        return "VideoFormat: [gauge: {}, aspect_ratio: {}, sound: {}; colour {}]".format(
            self.gauge, self.aspect_ratio, self.sound, self.colour)


class NonAVEntity(Creation):
    """
    Non-audiovisual objects in IMC can be pictures, photos, correspondence,
    books, periodicals etc.

    Attributes:
        date_created            The point or period of time associated with the
                                creation of the non-audiovisual creation
                                ("CCYY-MM-DD", "CCYY", CCYY-CCYY). If the
                                production year is unknown, the term “unknown”
                                should be added to indicate that research
                                regarding the production time has been
                                unsuccessful.
        non_av_type             The general type of the non-audiovisual
                                manifestation ("image" or "text").
        specific_type           This element further specifies the type of the
                                non-audiovisual entity.
        phisical_format_size    The dimensions of the physical object.
        colour                  This element can be used to indicate the colour
                                of a non-audiovisual object (e.g. "black and
                                white", "colour", "mixed").
    """
    date_created = ArrayProperty(StringProperty(), show=True)
    non_av_type = StringProperty(required=True,
                                 choices=codelists.NON_AV_TYPES,
                                 show=True)
    specific_type = StringProperty(
        required=True, choices=codelists.NON_AV_SPECIFIC_TYPES,
        show=True)
    phisical_format_size = ArrayProperty(StringProperty(), show=True)
    colour = StringProperty(choices=codelists.COLOUR, show=True)

# ANNOTATION
##############################################################################


class AnnotationCreatorRel(StructuredRel):
    when = DateTimeProperty(default=lambda: datetime.now(pytz.utc), show=True)


class Annotation(IdentifiedNode, AnnotationTarget):
    """Annotation class"""
    ANNOTATION_TYPES = (
        ('VQ', 'video quality'),
        ('VIM', 'video image motion'),
        ('TVS', 'temporal video segmentation'),
        ('TAG', 'tagging'),
        ('COM', 'commenting'),
        ('RPL', 'replying'),
        ('LNK', 'linking'),
        ('REP', 'reporting'),
        ('ASS', 'assessing'),
        ('DSC', 'describing'),
        ('BMK', 'bookmarking')
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
    private = BooleanProperty(default=False, show=True)
    embargo = DateProperty(show=True)
    source_item = RelationshipTo('Item', 'SOURCE', cardinality=One, show=True)
    creator = RelationshipTo(
        'User', 'IS_ANNOTATED_BY', cardinality=ZeroOrOne,
        model=AnnotationCreatorRel, show=True)
    generator = StringProperty(choices=AUTOMATIC_GENERATOR_TOOLS, show=True)
    bodies = RelationshipTo(
        'AnnotationBody', 'HAS_BODY', cardinality=ZeroOrMore, show=True)
    targets = RelationshipTo(
        'AnnotationTarget', 'HAS_TARGET', cardinality=OneOrMore, show=True)
    refined_selection = RelationshipTo(
        'FragmentSelector', 'REFINED_SELECTION', cardinality=ZeroOrOne)


class AnnotationBody(HeritableStructuredNode):
    annotation = RelationshipFrom('Annotation', 'HAS_BODY', cardinality=One)


class TextualBody(AnnotationBody):
    value = StringProperty(required=True, show=True)
    language = StringProperty(show=True)


class ResourceBody(AnnotationBody):
    iri = StringProperty(required=True, index=True, show=True)
    name = StringProperty(index=True, show=True)
    spatial = ArrayProperty(FloatProperty(), show=True)  # [lat, long]
    detected_objects = RelationshipFrom(
        'ODBody', 'CONCEPT', cardinality=ZeroOrMore)


class ODBody(AnnotationBody):
    """Detected Object"""
    object_id = StringProperty(required=True, show=True)
    confidence = FloatProperty(required=True, show=True)
    object_type = RelationshipTo('ResourceBody', 'CONCEPT', cardinality=One)


class ImageBody(AnnotationBody):
    pass


class AudioBody(AnnotationBody):
    audio_format = StringProperty(show=True)
    language = StringProperty(show=True)


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
        'VideoSegment', 'SEGMENT', cardinality=OneOrMore, show=True)


class VideoSegment(IdentifiedNode, AnnotationTarget):
    """Video Segment"""
    start_frame_idx = IntegerProperty(required=True, show=True)
    end_frame_idx = IntegerProperty(required=True, show=True)
    annotation_body = RelationshipFrom(
        'TVSBody', 'SEGMENT', cardinality=ZeroOrMore)
    within_shots = RelationshipTo('Shot', 'WITHIN_SHOT', cardinality=OneOrMore)


class Shot(VideoSegment):
    """Shot class"""
    shot_num = IntegerProperty(required=True, show=True)
    frame_uri = StringProperty()
    thumbnail_uri = StringProperty()
    timestamp = StringProperty(show=True)
    duration = FloatProperty(show=True)
    item = RelationshipFrom('Item', 'SHOT', cardinality=One)
    embedded_segments = RelationshipFrom(
        'VideoSegment', 'WITHIN_SHOT', cardinality=ZeroOrMore)
    revised_by = RelationshipTo('User', 'REVISED_BY', cardinality=ZeroOrMore,
                                model=RevisionRel)


class FragmentSelector(HeritableStructuredNode):
    annotation = RelationshipFrom(
        'Annotation', 'REFINED_SELECTION', cardinality=One)


class AreaSequenceSelector(FragmentSelector):
    """
    A sequence of regions for detected objects in a video segment frame by frame.

    e.g.
    [[x1,y1,w1,z1], [x2,y2,w2,z2], ...]
    """
    sequence = JSONProperty(required=True, show=True)
