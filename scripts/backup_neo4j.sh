#!/bin/bash

timestamp=`date +%s`
mkdir /tmp/$timestamp
cd /tmp/$timestamp

docker pause imc_backend_1
docker pause imc_celery_1

docker stop imc_neo4j_1

docker cp imc_neo4j_1:/data .

docker start imc_neo4j_1

docker unpause imc_backend_1
docker restart imc_backend_1

docker unpause imc_celery_1
docker restart imc_celery_1

tar -zcvf data.tar.gz data

cd -
mv /tmp/$timestamp/data.tar.gz .
rm -rf /tmp/$timestamp


#rm -rf data
~                    