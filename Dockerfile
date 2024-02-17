#code/Dockerfile
FROM debian:bookworm

# Copy our code to the firmware directory
WORKDIR /firmware
COPY . /firmware

# Update apt sources
RUN apt-get update

# Install python 3.11
RUN apt-get -y install python3.11
RUN apt-get -y install python3.11-dev
RUN apt-get -y install python3-pip
RUN pip install --upgrade pip --break-system-packages

# Install apt dependencies
RUN apt-get -y install portaudio19-dev
RUN apt-get -y install python3-pyaudio
RUN apt-get -y install ffmpeg

# Install python dependenices
# Copy our realsense library to the correct location in the container
RUN cp /firmware/dependencies/pyrealsense2.cpython-311-aarch64-linux-gnu.so /usr/local/lib/python3.11/dist-packages/pyrealsense2.cpython-311-aarch64-linux-gnu.so
RUN pip install -r requirements.txt --break-system-packages