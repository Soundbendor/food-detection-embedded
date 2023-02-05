# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

# Required to override warning when installing picamera python package
ENV READTHEDOCS=True

WORKDIR /pi_app

COPY requirements.txt requirements.txt

# Install dependencies for Pillow python package
RUN apt-get update && apt-get install -y gcc zlib1g-dev libjpeg-dev

RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "detect_foods.py" ]
