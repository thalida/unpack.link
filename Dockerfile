FROM python:3.7

MAINTAINER Thalida Noel "hello@thalida.com"

COPY Pipfile /Pipfile
COPY Pipfile.lock /Pipfile.lock

COPY unpack /unpack
COPY controller.py /controller.py

RUN pip install pipenv
RUN pipenv install --system --deploy

RUN touch /tmp/unpack_controller_logs.log

ENTRYPOINT ["python", "/controller.py"]
