
FROM rapydo/celery:0.6.1
MAINTAINER "Mattia D'Antonio <m.dantonio@cineca.it>"

# Backend/Celery build merged with:
# https://gitlab.hpc.cineca.it/usermanager/imedia-pipeline/blob/master/scripts/docker_python_runtime/Dockerfile
###################

RUN apt-get install -y ffmpeg libavcodec-extra libv4l-0

RUN pip install --upgrade --force-reinstall --no-cache-dir numpy

# download and install pre-compiled python opencv wrapper
ADD https://seafile.idmt.fraunhofer.de/f/46f83876ef/?raw=1 /usr/lib/python3/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so
RUN chmod a+r /usr/lib/python3/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so

# copy test script
# COPY ./test_python_installation.py /
# run the test script - if that fails, something went wrong
# RUN python3 /test_python_installation.py

