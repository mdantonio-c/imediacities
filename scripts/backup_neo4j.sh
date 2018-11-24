#!/bin/bash

# docker pause $(docker ps | grep imc_backend_ | awk {'print $1'})
# docker pause $(docker ps | grep imc_celery_ | awk {'print $1'})
docker stop $(docker ps | grep imc_neo4j_ | awk {'print $1'})

rsync -avP /home/ubuntu/imediacity/data/graphdata .

docker start $(docker ps | grep imc_neo4j_ | awk {'print $1'})
# docker unpause $(docker ps | grep imc_backend_ | awk {'print $1'})
# docker restart $(docker ps | grep imc_backend_ | awk {'print $1'})
# docker unpause $(docker ps | grep imc_celery_ | awk {'print $1'})
# docker restart $(docker ps | grep imc_celery_ | awk {'print $1'})


