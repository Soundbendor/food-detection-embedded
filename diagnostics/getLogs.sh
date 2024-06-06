#!/bin/bash
# Script to be run by cronjob every 12hrs (specified by the period variable, cronjob should match)
# Author: Will Richards

period='12h'
name='binsight-firmware'
server='sb-binsight.dri.oregonstate.edu:30080'

getAPIKey () {
    apiKey=$(cat ~/food-detection-embedded/src/config.secret | python -c "import sys, json; print(json.load(sys.stdin)['FASTAPI_CREDS']['apiKey'])")
}

getSerialNumber () {
    serialNumber=$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2)
}

# Check if the container is actaully running
if [ "$( docker container inspect -f '{{.State.Running}}' $name )" = "true" ]; then
    encodedData=$(docker logs --since=$period $name | base64 -w 0)
    encodedData="${encodedData//$'\n'/}"

    # Pull the API key from the config file and the serial number from /proc/cpuinfo
    getAPIKey
    getSerialNumber
    curl -v -X 'POST' "http://$server/api/upload_logs" -H "accept: application/json" -H"token: $apiKey" -H "Content-Type: application/json" -d "{\"deviceID\" : \"$serialNumber\", \"log\": \"$encodedData\"}"
else
    # TODO: Temporarily change cron job to trigger more frequently
    echo "Not running"
fi