#!/bin/bash
# Script to be run by cronjob every hour 30 minutes after the hour
# Author: Will Richards

name='binsight-firmware'
server='sb-binsight.dri.oregonstate.edu:30080'
lastUpdateFile='./diagnostics/lastUpdate.txt'

getAPIKey () {
    apiKey=$(cat ~/food-detection-embedded/src/config.secret | python -c "import sys, json; print(json.load(sys.stdin)['FASTAPI_CREDS']['apiKey'])")
}

checkAPIForUpdates () {
    updateResponse=$(curl -X 'GET' "http://$server/api/check_for_updates" -H "accept: application/json" -H "token: $apiKey" | python -c "import sys, json; print(json.load(sys.stdin)['lastUpdateTime'])")
}

getAPIKey

cd $HOME/food-detection-embedded

# If lastUpdated file doesn't exist we should write a 0 to it to start
if [ ! -f "$lastUpdateFile" ]; then
  echo "0" > "$lastUpdateFile"
fi

# Get the last updated value from the file
LAST_UPDATED=$(cat $lastUpdateFile)

# Hit the API to see if there was an update
checkAPIForUpdates

# if the time that the last device was updated is less than the last time an update was pushed we want to update
if (($LAST_UPDATED < $updateResponse)); then
    # Stop and remove the container if it is running
    if [ "$( docker container inspect -f '{{.State.Running}}' $name )" = "true" ]; then
        echo "Stopping running container"
        docker stop $name
        docker rm binsight-firmware
    fi

    # Download the updates from Github
    echo "Downloading updated firmware..."
    git pull

    # Update the last updated time
    echo "Rebuilding firmware..."
    echo $updateResponse > $lastUpdateFile

    # Rebuild and restart the container
    ./buildDocker.sh
    ./runDocker.sh    
    
else
    echo "Nothing to update"
fi
