FROM rapydo/backend:2.1

RUN apt-get update && \
    apt-get install --yes --no-install-recommends ffmpeg libavcodec-extra libv4l-0 libsm6 libxext6 imagemagick && \
    apt-get clean autoclean && \
    apt-get autoremove -y && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

RUN pip3 install --upgrade --force-reinstall --no-cache-dir numpy Pillow opencv-python
