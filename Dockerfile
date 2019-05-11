FROM python:3.5

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

RUN apt-get update
RUN apt-get -y install build-essential cmake pkg-config libx11-dev libatlas-base-dev libgtk-3-dev libboost-python-dev

COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

