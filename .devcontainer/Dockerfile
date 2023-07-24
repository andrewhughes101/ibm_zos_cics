FROM ubuntu:focal

ENV PY_VER=3.10
ENV LANG=en_US.UTF-8

ARG DEBIAN_FRONTEND=noninteractive

# Install essential packages
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y sudo software-properties-common curl git libffi-dev gcc locales && \
    apt-get update -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/*

# Ensure we have the correct Locale setup
RUN sed -i -e "s/# $LANG.*/$LANG UTF-8/" /etc/locale.gen && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=$LANG

# Install python
RUN add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update -y && \
    apt-get install -y python${PY_VER} && \
    apt-get update -y && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /var/cache/*

# Alias and symlink python
RUN alias python=python${PY_VER}
RUN alias python3=python${PY_VER}

RUN ln -s /usr/bin/python${PY_VER} /usr/local/bin/python

COPY ./pip_install.sh /tmp/pip_install.sh
RUN /bin/bash /tmp/pip_install.sh

RUN mkdir -p /root/ansible_collections
WORKDIR /root/ansible_collections
RUN git config --global --add safe.directory /root/ansible_collections