# -*- coding: utf-8 -*-

from restapi.utilities.logs import log
from restapi.connectors import get_debug_instance
from restapi.connectors.neo4j import NeoModel
graph = get_debug_instance(NeoModel)


def _is_public_domain(rs):
    return True if (
        rs == "02" or  # EU Orphan Work
        rs == "04" or  # In copyright - Non-commercial use permitted
        rs == "05" or  # Public Domain
        rs == "06" or  # No Copyright - Contractual Restrictions
        rs == "07" or  # No Copyright - Non-Commercial Use Only
        rs == "08" or  # No Copyright - Other Known Legal Restrictions
        rs == "09"     # No Copyright - United States
    ) else False


# default public access flag only to existing item with creation
results = graph.cypher(
    "MATCH (i:Item)-[:CREATION]->(c:Creation) RETURN i, c.rights_status")
if len(results) > 0:

    for item, rs in [(graph.Item.inflate(row[0]), row[1]) for row in results]:
        is_publicly_accessible = _is_public_domain(rs)
        item.public_access = is_publicly_accessible
        item.save()
        log.info("Item[{0}] - Right Status {1}. Is publicly accessible? {2}"
                 .format(item.uuid, rs, is_publicly_accessible))
