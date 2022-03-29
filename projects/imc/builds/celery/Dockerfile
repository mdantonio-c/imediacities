FROM rapydo/backend:2.2


RUN apt-get update -qq && \
    apt-get install --yes --no-install-recommends ffmpeg libavcodec-extra libv4l-0 libsm6 libxext6 imagemagick poppler-utils libfile-mimeinfo-perl libimage-exiftool-perl ghostscript libsecret-1-0 zlib1g-dev libjpeg-dev libmagic1 webp && \
    apt-get autoremove --yes && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/lib/cache /var/lib/log /tmp/*

RUN pip3 install --upgrade --force-reinstall --no-cache-dir numpy Pillow opencv-python preview-generator[3D]

RUN curl --silent https://storage.googleapis.com/dart-archive/channels/beta/release/2.17.0-182.1.beta/linux_packages/dart_2.17.0-182.1.beta-1_amd64.deb --output dart_amd64.deb \
    && dpkg -i dart_amd64.deb \
    && rm dart_amd64.deb \
    && git clone https://github.com/KhronosGroup/glTF-Validator.git \
    && cd glTF-Validator \
    && dart pub get \
    && dart run grinder exe \
    && cp build/bin/gltf_validator /usr/bin/gltf_validator