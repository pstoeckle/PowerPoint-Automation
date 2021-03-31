FROM python:3.9-buster

RUN apt-get update && apt-get upgrade -y
RUN apt install libreoffice -y
RUN pip install --upgrade pip
RUN useradd --create-home --shell /bin/bash libreoffice_user

# Install python lib.
COPY dist dist
RUN pip install dist/*.whl

ENV HOME=/home/libreoffice_user
USER libreoffice_user
WORKDIR /home/libreoffice_user
