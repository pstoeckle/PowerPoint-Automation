# SPDX-FileCopyrightText: 2022 Patrick Stöckle.
# SPDX-License-Identifier: Apache-2.0
# syntax=docker/dockerfile:1.3

FROM python:3.9-bullseye

LABEL author="Patrick Stöckle <patrick.stoeckle@posteo.de>"

ENV PATH="${PATH}:/home/libreoffice_user/.local/bin"

WORKDIR /

RUN apt-get update -qq \
    && apt-get upgrade -y -qq  \
    && apt-get install libreoffice=1:7.0.4-4+deb11u4 -y --no-install-recommends -qq \
    && apt-get autoremove -y -qq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash libreoffice_user

WORKDIR /home/libreoffice_user
USER libreoffice_user

COPY --chown=libreoffice_user dist dist

RUN pip install --no-cache-dir --upgrade pip==22.3.1 \
    && pip install --no-cache-dir dist/*.whl \
    && rm -rf dist \
    && powerpoint-automation --version
