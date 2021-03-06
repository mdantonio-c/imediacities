from datetime import datetime
from typing import Any, Dict, Optional

from restapi.rest.definition import EndpointResource
from restapi.utilities.logs import log


def string_from_timestamp(timestamp):
    if timestamp == "":
        return ""
    try:
        date = datetime.fromtimestamp(float(timestamp))
        return date.isoformat()
    except BaseException:
        log.warning("Errors parsing {}", timestamp)
        return ""


class IMCEndpoint(EndpointResource):
    def getJsonResponse(
        self,
        instance,
        relationship_depth=0,
        max_relationship_depth=1,
        relationship_name="",
        relationships_expansion=None,
    ):
        """
        Lots of meta introspection to guess the JSON specifications
        Very important: this method only works with customized neo4j models
        """

        verify_attribute = dict.get if isinstance(instance, dict) else hasattr

        res_id: Optional[str] = None
        if verify_attribute(instance, "uuid"):  # type: ignore
            res_id = str(instance.uuid)
        elif verify_attribute(instance, "id"):  # type: ignore
            res_id = str(instance.id)

        data = self.get_show_fields(instance)
        data["id"] = res_id

        # Relationships
        max_depth_reached = relationship_depth >= max_relationship_depth

        relationships = []
        if not max_depth_reached:

            relationships = instance.follow_relationships()

        # Used by IMC
        elif relationships_expansion is not None:
            for e in relationships_expansion:
                if e.startswith(f"{relationship_name}."):
                    rel_name_len = len(relationship_name) + 1
                    expansion_rel = e[rel_name_len:]
                    relationships.append(expansion_rel)

        for relationship in relationships:
            subrelationship = []

            if not hasattr(instance, relationship):
                continue
            rel = getattr(instance, relationship)
            for node in rel.all():
                if relationship_name == "":
                    rel_name = relationship
                else:
                    rel_name = f"{relationship_name}.{relationship}"
                subnode = self.getJsonResponse(
                    node,
                    relationship_depth=relationship_depth + 1,
                    max_relationship_depth=max_relationship_depth,
                    relationship_name=rel_name,
                    relationships_expansion=relationships_expansion,
                )

                # Verify if instance and node are linked by a
                # relationship with a custom model with fields flagged
                # as show=True. In this case, append relationship
                # properties to the attribute model of the node
                r = rel.relationship(node)
                attrs = self.get_show_fields(r)

                for k in attrs:
                    if k in subnode:
                        log.warning(
                            "Name collision {} on node {}, model {}, property model={}",
                            k,
                            subnode,
                            type(node),
                            type(r),
                        )
                    subnode[k] = attrs[k]

                subrelationship.append(subnode)

            if len(subrelationship) > 0:
                data[f"_{relationship}"] = subrelationship

        if "type" not in data:
            data["type"] = type(instance).__name__.lower()

        return data

    @staticmethod
    def get_show_fields(obj):

        fields = []
        if type(obj).__name__ == "User":
            fields = ["email", "name", "surname"]
        elif type(obj).__name__ == "Role":
            fields = ["name", "description"]
        elif hasattr(obj, "show_fields"):
            fields = obj.show_fields()

        verify_attribute = dict.get if isinstance(obj, dict) else hasattr

        attributes: Dict[str, Optional[Any]] = {}
        for key in fields:
            if verify_attribute(obj, key):  # type: ignore

                get_attribute = dict.get if isinstance(obj, dict) else getattr

                attribute = get_attribute(obj, key)  # type: ignore
                # datetime is not json serializable,
                # converting it to string
                # FIXME: use flask.jsonify
                if attribute is None:
                    attributes[key] = None
                elif isinstance(attribute, datetime):
                    dval = string_from_timestamp(attribute.strftime("%s"))
                    attributes[key] = dval
                else:

                    # Based on neomodel choices:
                    # http://neomodel.readthedocs.io/en/latest/properties.html#choices
                    choice_function = f"get_{key}_display"
                    if hasattr(obj, choice_function):
                        fn = getattr(obj, choice_function)
                        description = fn()

                        attribute = {"key": attribute, "description": description}
                    attributes[key] = attribute

        return attributes
