FROM python:3.6 as python

RUN apt-get update
RUN apt-get upgrade -y

# Installing environment and python deps
WORKDIR /app
RUN python3.6 -m venv venv
RUN ./venv/bin/pip install --upgrade pip
RUN ./venv/bin/pip install --upgrade setuptools
RUN ./venv/bin/pip install --upgrade wheel

# Installing HX711 for Jetson Nano
# github.com/kempei.hx711py-jetsonnano
RUN git clone https://github.com/kempei/hx711py-jetsonnano.git hx711
WORKDIR /app/hx711
RUN /app/venv/bin/python setup.py install

WORKDIR /app

# Installing other reqirements
COPY requirements.txt /app/
RUN ./venv/bin/pip install -r requirements.txt

USER root

CMD ["cp", "-r", "/app/venv/", "/out/"]
