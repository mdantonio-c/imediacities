FROM rapydo/backend:2.1

RUN apt-get update -qq && \
    apt-get install --yes --no-install-recommends ffmpeg libavcodec-extra libv4l-0 libsm6 libxext6 imagemagick && \
    apt-get autoremove --yes && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

RUN pip3 install --upgrade --force-reinstall --no-cache-dir numpy Pillow opencv-python
