#!/bin/bash
# Install dependencies
sudo apt-get install -y awscli jq
# Depends on being in the food waste directory
cd $HOME/food-detection-embedded
# Read values from the aws api key file, set as environments
aws configure set aws_access_key_id $(cat awskey_$HOSTNAME.secret | jq '.AccessKey.AccessKeyId' --raw-output)
aws configure set aws_secret_access_key $(cat awskey_$HOSTNAME.secret | jq '.AccessKey.SecretAccessKey' --raw-output)
