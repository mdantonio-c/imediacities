FROM rapydo/backend:0.7.6

MAINTAINER "Mattia D'Antonio <m.dantonio@cineca.it>"

RUN apt-get update && apt-get install -y ffmpeg libavcodec-extra libv4l-0 libsm6 libxext6 imagemagick

RUN pip3 install --upgrade --force-reinstall --no-cache-dir numpy Pillow opencv-python
