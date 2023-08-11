FROM nvcr.io/nvidia/l4t-base:35.4.1

RUN apt-get update
RUN apt-get upgrade -y

# Installing gstreamer dependencies
RUN apt-get install -y libgstreamer1.0-0 libgstreamer1.0-dev gstreamer1.0-tools gstreamer1.0-alsa gstreamer1.0-plugins-base gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libopencv-dev libgstreamer-plugins-base1.0-dev libegl1-mesa-dev libx11-dev libxext-dev

# Installing open cv deps
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

# Installing misc dependencies
RUN DEBIAN_FRONTEND=noninteractive TZ=America/New_York apt-get install -y wget curl git build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev tk-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
RUN apt-get install -y lbzip2 libcairo2 libgdk-pixbuf2.0-0 libgtk2.0-0 libjpeg8 libpng16-16 libtbb2 libtiff5 unzip

# Installing python 3.11
RUN apt-get install -y software-properties-common
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get install -y python3.11

RUN apt-get install -y python3-venv python3-pip python3-setuptools python3-distutils python3.11-venv

# Installing environment and python deps
WORKDIR /app
RUN python3.11 -m venv venv
RUN ./venv/bin/pip install --upgrade pip
RUN ./venv/bin/pip install --upgrade setuptools
RUN ./venv/bin/pip install --upgrade wheel

# Installing OpenCV2 with GSTREAMER support
WORKDIR /
RUN git clone --depth 1 --recurse-submodules --shallow-submodules https://github.com/opencv/opencv-python.git opencv-python
WORKDIR /opencv-python
ENV ENABLE_CONTRIB=0
ENV ENABLE_HEADLESS=1
ENV CMAKE_ARGS="-DWITH_GSTREAMER=ON"
RUN ./venv/bin/pip wheel . --verbose
RUN ./venv/bin/pip install opencv_python*.whl

WORKDIR /app

# Installing other reqirements
COPY requirements.txt /app/
RUN ./venv/bin/pip install -r requirements.txt

COPY . /app/

USER root

ENTRYPOINT ["./venv/bin/python3", "./src/main.py"]
