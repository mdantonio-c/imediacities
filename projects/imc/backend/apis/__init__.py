# -*- coding: utf-8 -*-

from datetime import datetime
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
        fields=None,
        skip_missing_ids=False,
        view_public_only=False,
        relationship_depth=0,
        max_relationship_depth=1,
        relationship_name="",
        relationships_expansion=None,
    ):
        """
        Lots of meta introspection to guess the JSON specifications
        Very important: this method only works with customized neo4j models
        """

        # Deprecated since 0.7.4
        # log.warning("Deprecated use of getJsonResponse")

        # Get id
        verify_attribute = hasattr
        if isinstance(instance, dict):
            verify_attribute = dict.get
        if verify_attribute(instance, "uuid"):
            res_id = str(instance.uuid)
        elif verify_attribute(instance, "id"):
            res_id = str(instance.id)
        else:
            res_id = None

        data = self.get_show_fields(
            instance, 'show_fields', view_public_only, fields
        )
        if not skip_missing_ids or res_id is not None:
            data['id'] = res_id

        # Relationships
        max_depth_reached = relationship_depth >= max_relationship_depth

        relationships = []
        if not max_depth_reached:

            relationships = instance.follow_relationships(
                view_public_only=view_public_only
            )

        # Used by IMC
        elif relationships_expansion is not None:
            for e in relationships_expansion:
                if e.startswith("{}.".format(relationship_name)):
                    rel_name_len = len(relationship_name) + 1
                    expansion_rel = e[rel_name_len:]
                    log.debug(
                        "Expanding {} relationship with {}",
                        relationship_name,
                        expansion_rel,
                    )
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
                    rel_name = "{}.{}".format(relationship_name, relationship)
                subnode = self.getJsonResponse(
                    node,
                    view_public_only=view_public_only,
                    skip_missing_ids=skip_missing_ids,
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
                attrs = self.get_show_fields(r, 'show_fields', view_public_only)

                for k in attrs:
                    if k in subnode:
                        log.warning(
                            "Name collision {} on node {}, model {}, property model={}",
                            k, subnode, type(node), type(r)
                        )
                    subnode[k] = attrs[k]

                subrelationship.append(subnode)

            if len(subrelationship) > 0:
                data["_{}".format(relationship)] = subrelationship

        if 'type' not in data:
            data['type'] = type(instance).__name__.lower()

        return data

    @staticmethod
    def get_show_fields(obj, function_name, view_public_only, fields=None):

        if fields is None:
            fields = []

        if type(obj).__name__ == 'User':
            fields = ['email', 'name', 'surname']

        elif type(obj).__name__ == 'Role':
            fields = ['name', 'description']

        elif len(fields) < 1:
            if hasattr(obj, function_name):
                fn = getattr(obj, function_name)
                fields = fn(view_public_only=view_public_only)

        verify_attribute = hasattr
        if isinstance(obj, dict):
            verify_attribute = dict.get

        attributes = {}
        for key in fields:
            if verify_attribute(obj, key):
                get_attribute = getattr
                if isinstance(obj, dict):
                    get_attribute = dict.get

                attribute = get_attribute(obj, key)
                # datetime is not json serializable,
                # converting it to string
                # FIXME: use flask.jsonify
                if attribute is None:
                    attributes[key] = None
                elif isinstance(attribute, datetime):
                    dval = string_from_timestamp(attribute.strftime('%s'))
                    attributes[key] = dval
                else:

                    # Based on neomodel choices:
                    # http://neomodel.readthedocs.io/en/latest/properties.html#choices
                    choice_function = "get_{}_display".format(key)
                    if hasattr(obj, choice_function):
                        fn = getattr(obj, choice_function)
                        description = fn()

                        attribute = {"key": attribute, "description": description}
                    attributes[key] = attribute

        return attributes
