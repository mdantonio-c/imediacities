#!/bin/bash

neo4j=$(docker ps | grep imc_neo4j_ | awk {'print $1'})
# backend=$(docker ps | grep imc_backend_ | awk {'print $1'})
# celery=$(docker ps | grep imc_celery_ | awk {'print $1'})
# docker pause $backend
# docker pause $celery
docker stop $neo4j

rsync -avP /home/ubuntu/imediacity/data/graphdata .

docker start $neo4j
# docker unpause $backend
# docker restart $backend
# docker unpause $celery
# docker restart $celery


