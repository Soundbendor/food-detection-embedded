#code/Dockerfile
FROM python:3.9-bookworm

# Copy our code to the firmware directory
WORKDIR /firmware
COPY ./requirements.txt /firmware/requirements.txt

# Update apt sources
RUN apt-get update

# Install python 3.9
RUN pip install --upgrade pip --break-system-packages

# Install apt dependencies
RUN apt-get -y install portaudio19-dev
RUN apt-get -y install python3-pyaudio
RUN apt-get -y install ffmpeg

# Install python dependenices
RUN pip install -r requirements.txt --break-system-packages

COPY . /firmware

# Compile whisper
WORKDIR /firmware/whisper.cpp
RUN make
WORKDIR /firmware