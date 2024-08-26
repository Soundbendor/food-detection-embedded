#!/bin/bash

cp $HOME/.aws .aws
docker build . -t binsight-firmware

