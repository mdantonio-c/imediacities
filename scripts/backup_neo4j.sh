#!/bin/bash
docker pause imc_neo4j_1
docker cp imc_neo4j_1:/data .
docker unpause imc_neo4j_1

# Wait for a complete sync of NFS volume...
# If this sleep is missing, folder size could be 0 and rsnapshot will not sync it!
sleep 120

