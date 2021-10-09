# NEOMODEL BASE CLASSES EXTENSION #
import inspect

from neomodel import AliasProperty as originalAliasProperty
from neomodel import ArrayProperty as originalArrayProperty
from neomodel import BooleanProperty as originalBooleanProperty
from neomodel import DateProperty as originalDateProperty
from neomodel import DateTimeProperty as originalDateTimeProperty
from neomodel import EmailProperty as originalEmailProperty
from neomodel import FloatProperty as originalFloatProperty
from neomodel import IntegerProperty as originalIntegerProperty
from neomodel import JSONProperty as originalJSONProperty
from neomodel import RelationshipFrom as originalRelationshipFrom
from neomodel import RelationshipTo as originalRelationshipTo
from neomodel import StringProperty as originalStringProperty
from neomodel import StructuredNode as originalStructuredNode
from neomodel import StructuredRel as originalStructuredRel
from neomodel import UniqueIdProperty as originalUniqueIdProperty
from neomodel.relationship_manager import RelationshipDefinition


def RelationshipTo(cls_name, rel_type, show=False, *args, **kwargs):
    """
    Ovveride of the RelationshipTo function from neomodel
    It call the original function and save into the returned object
    (instance of class RelationshipDefinition) the custom flags, to be used
    in the follow_relationships method of StructuredNode class
    """

    rel = originalRelationshipTo(cls_name, rel_type, *args, **kwargs)
    rel.show = show
    return rel


def RelationshipFrom(cls_name, rel_type, show=False, *args, **kwargs):
    """
    Ovveride of the RelationshipFrom function from neomodel
    It call the original function and save into the returned object
    (instance of class RelationshipDefinition) the custom flags, to be used
    in the follow_relationships method of StructuredNode class
    """

    rel = originalRelationshipFrom(cls_name, rel_type, *args, **kwargs)
    rel.show = show
    return rel


class myAttribProperty:
    """
    This class is used to save custom flags assigned to a property, to be used
    in the show_fields method of StructuredNode class.
    This class name is also used in the method above to filter out attributes
    not customized
    """

    show = False

    def save_extra_info(self, show=False):
        self.show = show


class StringProperty(originalStringProperty, myAttribProperty):  # type: ignore
    """
    Customized version of StringProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class IntegerProperty(originalIntegerProperty, myAttribProperty):  # type: ignore
    """
    Customized version of IntegerProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class FloatProperty(originalFloatProperty, myAttribProperty):  # type: ignore
    """
    Customized version of FloatProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class BooleanProperty(originalBooleanProperty, myAttribProperty):  # type: ignore
    """
    Customized version of BooleanProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class DateTimeProperty(originalDateTimeProperty, myAttribProperty):  # type: ignore
    """
    Customized version of DateTimeProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class DateProperty(originalDateProperty, myAttribProperty):  # type: ignore
    """
    Customized version of DateProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class ArrayProperty(originalArrayProperty, myAttribProperty):  # type: ignore
    """
    Customized version of ArrayProperty implemented in neomodel
    """

    def __init__(self, base_property=None, show=False, *args, **kwargs):

        self.save_extra_info(show)
        super().__init__(base_property, *args, **kwargs)


class JSONProperty(originalJSONProperty, myAttribProperty):  # type: ignore
    """
    Customized version of JSONProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class EmailProperty(originalEmailProperty, myAttribProperty):  # type: ignore
    """
    Customized version of EmailProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class AliasProperty(originalAliasProperty, myAttribProperty):  # type: ignore
    """
    Customized version of AliasProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class UniqueIdProperty(originalUniqueIdProperty, myAttribProperty):  # type: ignore
    """
    Customized version of UniqueIdProperty implemented in neomodel
    """

    def __init__(self, show=False, *args, **kwargs):
        self.save_extra_info(show)
        super().__init__(*args, **kwargs)


class StructuredRel(originalStructuredRel):
    """
    Customized version of StructuredRel class implemented in neomodel
    This class exposes the show_fields method.
    This method uses custom flags set in myAttribProperty instances
    """

    @classmethod
    def show_fields(cls):

        fields_to_show = []

        classes = inspect.getmro(cls)
        for cls_name in classes:
            if cls_name.__name__ == "StructuredRel":
                break

            for c in cls_name.__dict__:
                attrib = getattr(cls, c)
                # print("fields:", cls.__name__, attrib)
                if not isinstance(attrib, myAttribProperty):  # type: ignore
                    continue
                if not attrib.show:
                    continue

                fields_to_show.append(c)
        return fields_to_show


class StructuredNode(originalStructuredNode):
    """
    Customized version of StructuredNode class implemented in neomodel
    This class exposes the show_fields and follow_relationships methods.
    These methods use custom flags set in myAttribProperty instances and in
    RelationshipDefinition instances (as modified by the custom functions
    RelationshipTo and RelationshipFrom)

    Note: abstract nodes to be used as base have to use a configuration like:
    http://j.mp/2o54N47 (neomodel readthedocs)
    """

    __abstract_node__ = True

    @classmethod
    def show_fields(cls):

        fields_to_show = []

        classes = inspect.getmro(cls)
        for cls_name in classes:
            if cls_name.__name__ == "StructuredNode":
                break

            for c in cls_name.__dict__:
                attrib = getattr(cls, c)
                # print("fields:", cls.__name__, attrib)
                if not isinstance(attrib, myAttribProperty):
                    continue
                if not attrib.show:
                    continue

                fields_to_show.append(c)
        return fields_to_show

    @classmethod
    def follow_relationships(cls):

        relationship_to_follow = []

        classes = inspect.getmro(cls)
        for cls_name in classes:
            if cls_name.__name__ == "StructuredNode":
                break

            for c in cls_name.__dict__:
                attrib = getattr(cls, c)
                if not isinstance(attrib, RelationshipDefinition):
                    continue
                if hasattr(attrib, "show"):
                    show = getattr(attrib, "show")
                else:
                    show = False
                if not show:
                    continue

                relationship_to_follow.append(c)
        return relationship_to_follow
