#!/bin/bash
export MEDIA_IN=$1
export MEDIA_OUT=$2
export TIME_MAX=$3
ffmpeg   -ss 0     -i $MEDIA_IN      -c copy     -t $TIME_MAX      $MEDIA_OUT
