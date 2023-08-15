FROM python:3.6 as python

FROM nvcr.io/nvidia/l4t-base:35.4.1 as build

RUN apt-get update
RUN apt-get upgrade -y

# Installing misc dependencies
RUN DEBIAN_FRONTEND=noninteractive TZ=America/New_York apt-get install -y wget curl git build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev tk-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev

# Installing GStreamer Deps
RUN apt-get install -y \
  libgstreamer1.0-0 libgstreamer1.0-dev gstreamer1.0-tools \
  gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
  libopencv-dev libgstreamer-plugins-base1.0-dev libegl1-mesa-dev \
  libx11-dev libxext-dev libmnl-dev
RUN \
  apt-get install \
  lbzip2 xorg-dev \
  cmake unzip \
  libgtk2.0-dev pkg-config \
  libavcodec-dev \
  libgstreamer1.0-dev \
  libgstreamer-plugins-base1.0-dev \
  libjpeg-dev \
  libpng-dev \
  libtiff-dev -y

# Required for CV2 to work properly
ENV OPENBLAS_CORETYPE="ARMV8"
ENV PATH="${PATH}:/usr/local/host:/usr/local/host/tegra:/usr/local/bin:/usr/local/lib"
ENV LD_LIBRARY_PATH="${PATH}:${LD_LIBRARY_PATH}"
ENV GST_PLUGIN_PATH="$PATH"

# Copying Python3.6
COPY --from=python /usr/local/lib/ /usr/local/lib
COPY --from=python /usr/local/bin/ /usr/local/bin

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

COPY . /app/

USER root

ENTRYPOINT ["./venv/bin/python3", "./src/main.py"]
