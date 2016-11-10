# darcmail
#
# VERSION               0.0.5

FROM phusion/baseimage
MAINTAINER Jeremy Gibson <jeremy.gibson@ncdcr.gov>

RUN apt-get update && apt-get install -y python3 python3-setuptools
RUN easy_install3 pip
RUN pip install lxml PyYAML

RUN useradd -ms /bin/bash tomes
RUN echo 'tomes:tomespass' | chpasswd
RUN mkdir -p /home/tomes/data

ADD DarcMailCLI /home/tomes/DarcMailCLI