FROM python:3.6 as python

RUN apt-get update
RUN apt-get upgrade -y

# Installing environment and python deps
WORKDIR /app
RUN python3.6 -m venv venv
RUN ./venv/bin/pip install --upgrade pip
RUN ./venv/bin/pip install --upgrade setuptools
RUN ./venv/bin/pip install --upgrade wheel

WORKDIR /app

# Installing other reqirements
COPY requirements.txt /app/
RUN ./venv/bin/pip install -r requirements.txt

USER root

CMD ["cp", "-r", "/app/venv/", "/out/"]
