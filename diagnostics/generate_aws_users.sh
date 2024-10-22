#!/bin/bash

for i in $(seq 3 55); do
  host="smartbin$i"
  echo $host
  aws iam create-user --user-name $host
  aws iam add-user-to-group --group-name compost-bin --user-name $host
  aws iam create-access-key --user-name $host >"creds/awskey_$host.secret"
done
