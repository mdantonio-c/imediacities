#!/bin/bash

docker pause imc_backend_1
docker pause imc_celery_1
docker stop imc_neo4j_1

# docker cp imc_neo4j_1:/data .

rsync -avP /home/ubuntu/imediacity/data/graphdata .

docker start imc_neo4j_1
docker unpause imc_backend_1
docker restart imc_backend_1
docker unpause imc_celery_1
docker restart imc_celery_1

#timestamp=`date +%s`
#mkdir /tmp/$timestamp
#tar -zcvf graphdata.tar.gz graphdata

