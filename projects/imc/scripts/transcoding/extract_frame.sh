#!/bin/bash
export MEDIA=$1
export N=$2
ffmpeg -i $MEDIA -vf "select=gte(n\,${N})" -vframes 1 ${MEDIA}.${N}.jpg
