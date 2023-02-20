#!/usr/bin/env bash

command_arg=$1

function pull_changes {
    echo 'Pulling changes from GitHub...'
    cd food-detection-embedded/
    git pull --ff-only

    echo 'Installing dependencies...'
    ./venv/bin/pip3 install -qr requirements.txt

    cd ..
}

function run_detection {
    echo 'Running detections....'
    echo '(press ctrl+c to stop)'
    sudo ./food-detection-embedded/venv/bin/python3 ./food-detection-embedded/detect_foods.py $2
}

if [ "${command_arg}" == "install" ]; then
    git clone https://github.com/Soundbendor/food-detection-embedded.git

    mkdir archive_detection_images
    mkdir archive_check_focus_images
    mkdir logs

    echo 'Creating virtual environment for dependencies...'
    cd ./food-detection-embedded
    python3 -m venv venv
    echo 'Installing dependencies (takes a minute)...'
    ./venv/bin/pip3 install -qr requirements.txt
    
    cd ..
    echo ''
    echo 'Done. Now use `./food_detector.sh detect` to detect some foods!'

elif [ "${command_arg}" == "pull" ]; then
    pull_changes

    echo ''
    echo 'Done. Now use `./food_detector.sh detect` to detect some foods!'

elif [ "${command_arg}" == "pull+detect" ]; then
    pull_changes
    run_detection

elif [ "${command_arg}" == "detect" ]; then
    run_detection

elif [ "${command_arg}" == "focus" ]; then
    echo 'Checking camera focus...'
    echo '(press ctrl+c to stop)'
    sudo ./food-detection-embedded/venv/bin/python3 ./food-detection-embedded/check_focus.py $2

elif [ "${command_arg}" == "clean" ]; then
    echo 'This will delete all files and code in the repo (but keep the archive files). Are you sure you want to proceed? (y/n)'
    read decision
    echo ''
    if [ "${decision}" == "yes" ] || [ "${decision}" == "y" ]; then
        rm -rf ./food-detection-embedded
        echo 'All files removed.'
    else
        echo 'No files removed.'
    fi
else
    echo '`${command_arg}` not recognized as a command.'
    echo 'Please use: `detect`, `focus`, `pull`, `clean`, or `install`.'
fi
