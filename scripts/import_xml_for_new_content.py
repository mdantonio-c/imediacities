"""
Procedure to start processing for those records already present in db and for
which the contents have not been ingested.
The current bulk update procedure does not allow for this use case, so that an
ad-hoc procedure is implemented here.

Run this procedure inside celery container
For instance:
python3 import_xml_for_new_content.py
    --metadata_set mct
    --domain_name imediacities.hpc.cineca.it
    --token 'Bearer eyJ0eXAiOiJ..'
"""

import click
import requests
from restapi.connectors import get_debug_instance
from restapi.connectors.neo4j import NeoModel
from restapi.utilities.logs import log


@click.command()
@click.option(
    "--metadata_set",
    prompt="Archive code to be imported",
    help="Name of the group set to be imported (e.g. ofm, ccb, etc.)",
)
@click.option("--domain_name", prompt="API domain name", help="API domain name")
@click.option("--token", prompt="Authentication token", help="Authentication token")
def import_xml(metadata_set, domain_name, token):
    log.info(f"Import XML with no content bound for domain: {domain_name}")
    graph = get_debug_instance(NeoModel)

    # get available groups
    groups = [row[0] for row in graph.cypher("MATCH (g:Group) return g.shortname")]

    if metadata_set not in groups:
        log.exit(f"Please specify a valid metadata_set. Allowed values {groups}")

    # Extract the filename of those MetaStages for which the content has not yet been ingested
    results = graph.cypher(
        "MATCH (m:MetaStage)<-[:META_SOURCE]-(i:Item)-[:IS_OWNED_BY]-(g:Group {{shortname:'{group}'}})"
        " WHERE NOT (i)-[:CONTENT_SOURCE]-()"
        " RETURN m.filename".format(group=metadata_set)
    )
    if not results:
        log.info("Nothing to import")
    else:
        succeed = 0
        failed = 0
        # for each record start an import in "fast" mode
        for filename in [row[0] for row in results]:
            payload = {"filename": filename, "mode": "fast"}
            headers = {"Authorization": token}
            resp = requests.post(
                f"https://{domain_name}/api/stage", headers=headers, data=payload
            )
            try:
                resp.raise_for_status()
            except requests.exceptions.HTTPError as http_error:
                log.warning(
                    f"Imported record: {filename}. STATUS CODE {resp.status_code}"
                )
                log.warning(http_error)
                failed += 1
                continue
            log.info(f"Imported record: {filename}. STATUS CODE {resp.status_code}")
            succeed += 1
        log.info(f"Imported records: SUCCEED {succeed}, FAILED {failed}")


if __name__ == "__main__":
    import_xml()
