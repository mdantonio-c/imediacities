"""
Procedura per importare tag automatici

Run this procedure inside celery container
For instance:
python3 import_automatic_tags.py
    --metadata_set mct
    --domain_name imediacities.hpc.cineca.it
    --token 'Bearer eyJ0eXAiOiJ..'
    --tool object-detection
"""

import click
import requests
from restapi.connectors import get_debug_instance
from restapi.connectors.neo4j import NeoModel
from restapi.utilities.logs import log

tools = ["object-detection", "building-recognition"]


@click.command()
@click.option(
    "--metadata_set",
    prompt="Archive code to be imported",
    help="Name of the group set to be imported (e.g. ofm, ccb, etc.)",
)
@click.option("--domain_name", prompt="API domain name", help="API domain name")
@click.option("--token", prompt="Authentication token", help="Authentication token")
@click.option(
    "--tool",
    prompt="Tool to be launched",
    help="Tool to be launched (e.g. object-detection)",
)
def import_automatic_tags(metadata_set, domain_name, token, tool):
    log.info(
        "Import automatic tags [{tool}] for group: {group}".format(
            group=metadata_set, tool=tool
        )
    )

    graph = get_debug_instance(NeoModel)

    # get available groups
    groups = [row[0] for row in graph.cypher("MATCH (g:Group) return g.shortname")]

    if metadata_set not in groups:
        log.exit(f"Please specify a valid metadata_set. Allowed values {groups}")
    if tool not in tools:
        log.exit(f"Please specify a valid tool. Allowed values {tools}")

    # Extract the filename of those MetaStages for which the content has not yet been ingested
    results = graph.cypher(
        "MATCH (c:Creation)<-[:CREATION]-(i:Item)-[:IS_OWNED_BY]-(g:Group {{shortname:'{group}'}}) "
        "MATCH (i)-[:CONTENT_SOURCE]->(:ContentStage {{status:'COMPLETED'}}) "
        "RETURN i, c.uuid".format(group=metadata_set)
    )
    if not results:
        log.info("Nothing to import")
    else:
        skipped = 0
        failed = 0
        succeed = 0
        for item, uuid in [(graph.Item.inflate(row[0]), row[1]) for row in results]:
            payload = {"tool": tool}
            headers = {"Authorization": token}
            endpoint_type = "videos" if item.item_type == "Video" else "images"
            url = f"https://{domain_name}/api/{endpoint_type}/{uuid}/tools"
            resp = requests.post(url, headers=headers, data=payload)
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as http_error:
                log.warning(
                    f"Imported automatic tags for item: {item.uuid}. STATUS CODE {resp.status_code}"
                )
                log.warning(http_error)
                if resp.status_code == 409:
                    skipped += 1
                else:
                    failed += 1
                continue
            log.info(
                f"Imported automatic tags for item: {item.uuid}. STATUS CODE {resp.status_code}"
            )
            succeed += 1
        log.info(
            f"Imported items: SUCCEED {succeed}, FAILED {failed}, SKIPPED {skipped}"
        )


if __name__ == "__main__":
    import_automatic_tags()
