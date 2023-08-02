FROM python:3.11

# Installing Other stuff
RUN apt update
RUN apt upgrade -y
RUN DEBIAN_FRONTEND=noninteractive TZ=America/New_York apt install -y wget curl build-essential libncursesw5-dev libssl-dev libsqlite3-dev tk-dev libgdbm-dev tk-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
RUN apt install -y python3-venv

WORKDIR /app
RUN python3.11 -m venv venv
RUN ./venv/bin/pip install --upgrade pip
RUN ./venv/bin/pip install --upgrade setuptools
RUN ./venv/bin/pip install --upgrade wheel
COPY requirements.txt /app/
RUN ./venv/bin/pip install -r requirements.txt

COPY . /app/

USER root

ENTRYPOINT ["./venv/bin/python3", "./src/main.py"]
