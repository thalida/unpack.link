FROM python:3.7

LABEL maintainer="hello@thalida.com"

COPY . /unpack
WORKDIR /unpack

RUN pip install pipenv
RUN pipenv install --system --deploy

ENTRYPOINT ["python", "controller.py"]
