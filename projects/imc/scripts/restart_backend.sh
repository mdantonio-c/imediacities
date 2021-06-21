#!/bin/bash

docker restart $(docker ps | grep imc_backend_ | awk {'print $1'})
