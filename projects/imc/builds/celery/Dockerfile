
FROM rapydo/celery:0.6.0
MAINTAINER "Mattia D'Antonio <m.dantonio@cineca.it>"

# Backend/Celery build merged with:
# https://gitlab.hpc.cineca.it/usermanager/imedia-pipeline/blob/master/scripts/docker_python_runtime/Dockerfile

RUN apt-get install -y ffmpeg libavcodec-extra libv4l-0 libsm6 libxext6 imagemagick

RUN pip install --upgrade --force-reinstall --no-cache-dir numpy Pillow opencv-python

# download and install pre-compiled python opencv wrapper
# ADD https://seafile.idmt.fraunhofer.de/f/46f83876ef/?raw=1 /usr/local/lib/python3.6/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so 
# RUN chmod a+r /usr/local/lib/python3.6/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so 

# REMOVE ME ON RAPYDO:0.6.1
RUN ln -s /usr/bin/python3.6 /usr/bin/python3

RUN export LD_LIBRARY_PATH=/opt/idmt/lib/:$LD_LIBRARY_PATH

