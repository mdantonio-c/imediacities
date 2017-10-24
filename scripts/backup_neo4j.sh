#!/bin/bash

#Simply pausing neo4j is not enough

#docker pause imc_neo4j_1
#docker cp imc_neo4j_1:/data .
#docker unpause imc_neo4j_1

docker pause imc_backend_1
docker pause imc_celery_1
docker stop imc_neo4j_1

docker cp imc_neo4j_1:/data .

docker start imc_neo4j_1
docker unpause imc_celery_1
docker unpause imc_backend_1

