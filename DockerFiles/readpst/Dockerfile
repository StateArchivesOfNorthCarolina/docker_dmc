# readpst
#
# VERSION               0.0.5

FROM phusion/baseimage
MAINTAINER Jeremy Gibson <jeremy.gibson@ncdcr.gov>

RUN apt-get update && apt-get install -y readpst

RUN useradd -ms /bin/bash tomes
RUN echo 'tomes:tomespass' | chpasswd
RUN mkdir -p /home/tomes/data