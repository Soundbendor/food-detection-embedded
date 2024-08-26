#!/bin/bash

cp -r $HOME/.aws .aws
docker build . -t binsight-firmware

