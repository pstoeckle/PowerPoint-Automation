FROM python:3.9-bullseye

ARG COMMIT=""
ARG COMMIT_SHORT=""
ARG BRANCH=""
ARG TAG=""

LABEL author="Patrick Stöckle <patrick.stoeckle@tum.de>"
LABEL edu.tum.i4.powerpoint-automation.commit=${COMMIT}
LABEL edu.tum.i4.powerpoint-automation.commit-short=${COMMIT_SHORT}
LABEL edu.tum.i4.powerpoint-automation.branch=${BRANCH}
LABEL edu.tum.i4.powerpoint-automation.tag=${TAG}

ENV COMMIT=${COMMIT}
ENV COMMIT_SHORT=${COMMIT_SHORT}
ENV BRANCH=${BRANCH}
ENV TAG=${TAG}

RUN apt-get update -qq \
    && apt-get upgrade -y -qq  \
    && apt-get install libreoffice -y --no-install-recommends -qq \
    && apt-get autoremove -y -qq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash libreoffice_user

WORKDIR /home/libreoffice_user
COPY dist dist

RUN chown libreoffice_user dist

USER libreoffice_user

RUN pip install --no-cache-dir --upgrade pip==21.3.1 \
    && pip install --no-cache-dir dist/*.whl \
    && rm -rf dist

ENV PATH="${PATH}:/home/libreoffice_user/.local/bin"

RUN powerpoint-automation --version
