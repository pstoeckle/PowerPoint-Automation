FROM python:3.9-buster

RUN apt-get update && apt-get upgrade -y
RUN apt install libreoffice -y

RUN pip install --upgrade pip
COPY dist dist
RUN pip install dist/*.whl

RUN useradd --create-home --shell /bin/bash libreoffice_user
ENV HOME=/home/libreoffice_user
USER libreoffice_user
WORKDIR /home/libreoffice_user
