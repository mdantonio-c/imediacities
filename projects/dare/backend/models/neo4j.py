from neomodel import (  # UniqueIdProperty
    AliasProperty,
    ArrayProperty,
    BooleanProperty,
    DateProperty,
    DateTimeProperty,
    FloatProperty,
    IntegerProperty,
    JSONProperty,
    OneOrMore,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
    StructuredRel,
    ZeroOrMore,
)
from restapi.connectors.neo4j.types import IdentifiedNode, TimestampedNode

# from restapi.utilities.logs import log


# Extension of core models


class UserCustom(IdentifiedNode):
    __abstract_node__ = True


class GroupCustom(IdentifiedNode):
    __abstract_node__ = True


class RelationTest(StructuredRel):
    pp = StringProperty()


class JustATest(TimestampedNode):
    p_str = StringProperty(required=True)
    p_int = IntegerProperty()
    p_arr = ArrayProperty()
    p_json = JSONProperty()
    p_float = FloatProperty()
    p_date = DateProperty()
    p_dt = DateTimeProperty()
    p_bool = BooleanProperty()
    p_alias = AliasProperty()

    test1 = RelationshipFrom(
        "restapi.connectors.neo4j.models.User",
        "TEST",
        cardinality=ZeroOrMore,
        model=RelationTest,
    )

    test2 = RelationshipFrom(
        "restapi.connectors.neo4j.models.User",
        "TEST2",
        cardinality=ZeroOrMore,
        model=RelationTest,
    )
