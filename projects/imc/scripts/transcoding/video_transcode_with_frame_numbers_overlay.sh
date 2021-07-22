#!/bin/bash
export MEDIA_IN=$1
export MEDIA_OUT=$2
export FPS=$3
export FONT=/usr/share/fonts/truetype/ubuntu-font-family/UbuntuMono-B.ttf
/usr/bin/ffmpeg -hide_banner -nostdin -y \
-i $MEDIA_IN \
-strict experimental \
-vf "drawtext=fontfile=$FONT: text=%{n}: x=10: y=10: fontsize=50: fontcolor=white: box=1: boxcolor=0x00000099"  \
-vcodec libx264 -crf 15.0 -pix_fmt yuv420p -coder 1 -rc_lookahead 60 -r $FPS  \
-g $FPS \
-acodec aac -b:a 128k \
$MEDIA_OUT

