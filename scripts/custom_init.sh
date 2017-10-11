#!/bin/bash

# This script has been moved into the script folder
# execute as: bash scripts/custom_init.sh

echo "Copying example video"

cp -r scripts/analysis/test_data/00000000-0000-0000-00000000000000000 data/imediastuff/

echo "**********************************"
echo "* INSTALLING FRAUNHOFER SOFTWARE *"
echo "**********************************"

cd submodules

echo "Removing previous installation, if any"
rm -rf imedia-pipeline

echo "Cloning imedia-pipeline repository, please provide your CINECA gitlab credentials"
git clone https://gitlab.hpc.cineca.it/usermanager/imedia-pipeline.git

cd imedia-pipeline/tools/
tag=`git tag | grep tools | tail -1`
echo "Selected tag: $tag"
git checkout $tag

echo "Please provide the Fraunhofer password"
read -s fraunhofer_password
sudo ./setup_idmt_tools.sh -m remove
sudo ./setup_idmt_tools.sh -m install -p $fraunhofer_password

echo "Init completed"

