from restapi.connectors import get_debug_instance
from restapi.connectors.neo4j import NeoModel
from restapi.utilities.logs import log

graph = get_debug_instance(NeoModel)


def _is_public_domain(rs):
    return (
        True
        if (
            rs == "02"
            or rs == "04"  # EU Orphan Work
            or rs == "05"  # In copyright - Non-commercial use permitted
            or rs == "06"  # Public Domain
            or rs == "07"  # No Copyright - Contractual Restrictions
            or rs == "08"  # No Copyright - Non-Commercial Use Only
            or rs  # No Copyright - Other Known Legal Restrictions
            == "09"  # No Copyright - United States
        )
        else False
    )


# default public access flag only to existing item with creation
results = graph.cypher(
    "MATCH (i:Item)-[:CREATION]->(c:Creation) RETURN i, c.rights_status"
)
if len(results) > 0:

    for item, rs in [(graph.Item.inflate(row[0]), row[1]) for row in results]:
        is_publicly_accessible = _is_public_domain(rs)
        item.public_access = is_publicly_accessible
        item.save()
        log.info(
            "Item[{}] - Right Status {}. Is publicly accessible? {}".format(
                item.uuid, rs, is_publicly_accessible
            )
        )
