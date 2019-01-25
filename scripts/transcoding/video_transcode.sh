#!/bin/bash
export MEDIA_IN=$1
export MEDIA_OUT=$2
export FPS=$3
/usr/bin/ffmpeg -hide_banner -nostdin -y \
-i $MEDIA_IN \
-vf yadif=0:-1:0 \
-strict experimental \
-vcodec libx264 -crf 15.0 -pix_fmt yuv420p -coder 1 -rc_lookahead 60 -r $FPS  \
-g $FPS
-acodec aac -b:a 128k \
$MEDIA_OUT
