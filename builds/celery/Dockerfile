
# Backend/Celery build merged with:
# https://gitlab.hpc.cineca.it/usermanager/imedia-pipeline/blob/master/scripts/docker_python_runtime/Dockerfile
###################
# FROM eudatb2stage/apiserver:neo4j3
FROM ubuntu:16.04
# FROM ubuntu:17.04
MAINTAINER "Mattia D'Antonio <m.dantonio@cineca.it>"

##################################
# FROM Fraunhofer
#up to date system 
RUN apt-get -y update \
 && apt-get -y upgrade 
##################################

###################
# APT
RUN apt-get update && apt-get install -y \
    # utils
    bash less vim curl wget telnet git jq \

    ##################################
    # Fraunhofer libraries
    python3 \
    ffmpeg \
    libv4l-0 \
    ##################################
    # latest python
    # python3.6 \
    # make this version the official python for anyone
    # && cd /usr/bin && ln -s python3.6 python \
##################################
    && apt-get autoremove && apt-get clean \
    && echo "done"

###################
# PIP

WORKDIR /tmp
COPY requirements.txt /tmp/
RUN wget -q https://bootstrap.pypa.io/get-pip.py \
    && python3 get-pip.py && rm *.py
    # && python get-pip.py && rm *.py

# for Fraunhofer: in requirements.txt added numpy
RUN pip3 install --upgrade \
    --force-reinstall --no-cache-dir -r requirements.txt

###################
# TODO: decide about a main user recipe for containers
ENV APIUSER developer
# main user for launching the apis
RUN useradd -r -M -d $CERTDIR/home -s /bin/bash -p ! $APIUSER
###################
# Closing entrypoint

RUN mkdir /code
WORKDIR /code
RUN mkdir /docker-entrypoint.d/
RUN echo "Entrylevel" && \
    echo "echo\necho 'Run Flask server as ($APIUSER) with the command:'\necho '$ httpapi'" >> /root/.bashrc && \
    echo "echo\necho 'Run tests with $ cd /code; nose2 -F [test.FOLDER]'\n" \
    >> /root/.bashrc

COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint
RUN chmod +x /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]
CMD ["rest"]
ENV PAGER less
ENV TERM=xterm-256color
ENV PYTHONIOENCODING="utf-8"
# Flask port
EXPOSE 5000


##################################
# FROM Fraunhofer
# download and install pre-compiled python opencv wrapper
# Fraunhofer version:
ADD https://seafile.idmt.fraunhofer.de/f/46f83876ef/?raw=1 /usr/lib/python3/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so
# Mattia version:
# ADD https://seafile.idmt.fraunhofer.de/f/46f83876ef/?raw=1 /usr/local/lib/python3.6/dist-packages/cv2.cpython-35m-x86_64-linux-gnu.so 
##################################


##################################
# FROM Fraunhofer
# copy test script
COPY ./test_python_installation.py /
# run the test script - if that fails, something went wrong
RUN python3 /test_python_installation.py
##################################

###################
# UWSGI
ENV UWSGI_LOGS /var/log/uwsgi
ENV UWSGI_RUN /var/run/uwsgi
ENV MYUWSGI_HOME /tmp/uwsgi
RUN mkdir -p $UWSGI_LOGS
RUN mkdir -p $UWSGI_RUN
RUN chown -R www-data:www-data $UWSGI_LOGS $UWSGI_RUN
COPY nginx_uwsgi.conf /etc/nginx/sites-available/default
ENV UWSGI_MASTER ${MYUWSGI_HOME}/uwsgi_starter.ini
COPY uwsgi.ini ${UWSGI_MASTER}
COPY launch_uwsgi.sh /usr/local/bin/myuwsgi
RUN chmod +x /usr/local/bin/myuwsgi
# # remove nginx defaults
# RUN rm -rf /etc/nginx/sites-enabled

###################
# variables
ENV PAGER less
ENV TERM=xterm-256color
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8
ENV PYTHONIOENCODING="utf-8"
ENV FLASK_PORT 5000
ENV JWT_APP_SECRETS /jwts
EXPOSE $FLASK_PORT

######################
# alias
RUN echo "alias dev=\"HOME=/tmp su -p \$APIUSER\"" >> /root/.bash_aliases
RUN echo "alias testapi=\"su -p \$APIUSER -c 'export HOME=/tmp; cd /code; nose2 -F '\"" >> /root/.bash_aliases

RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; ./tests.sh'" > /usr/local/bin/testwithcoverage && chmod +x /usr/local/bin/testwithcoverage
RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; flask run --with-threads -h 0.0.0.0 -p $FLASK_PORT '" > /usr/local/bin/rapydo && chmod +x /usr/local/bin/rapydo
RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; FLASK_DEBUG=0 ./manage.py init'" > /usr/local/bin/initialize && chmod +x /usr/local/bin/initialize
RUN echo "#!/bin/bash\\nsu -p \$APIUSER -c 'export HOME=/tmp; cd /code; FLASK_DEBUG=0 ./manage.py destroy'" > /usr/local/bin/demolition && chmod +x /usr/local/bin/demolition

######################
# instructions
RUN echo "Entrylevel" && \
    echo "echo\necho 'Run Flask server as ($APIUSER) with the command:'\necho '$ rapydo'" >> /root/.bashrc && \
    echo "echo\necho 'Run tests also with:\n$ testapi [test.FOLDER]\n'\n" \
        >> /root/.bashrc \
    && echo "echo\necho '$ python run.py'" > /tmp/.bashrc

###################
# closing entrypoint

RUN mkdir /code
WORKDIR /code
RUN mkdir /docker-entrypoint.d/
COPY ./docker-entrypoint.sh /usr/local/bin/docker-entrypoint
ENTRYPOINT ["docker-entrypoint"]

# RUN flower -A flask_ext.flask_celery.worker.celery_app \
#         --broker=amqp://guest:guest@queue:5672//
CMD ["rest"]
# CMD ["celery worker -c 1 -A flask_ext.flask_celery.worker.celery_app"]
