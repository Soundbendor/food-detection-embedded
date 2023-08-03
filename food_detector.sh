#!/usr/bin/env bash

dir="$(dirname "$0")"
dir_absolute="$(readlink -m "$dir")"
cd "$dir"

command_arg=$1
MAIN="./src/main.py"

function pull_changes {
    echo 'Pulling changes from GitHub...'
    git pull --ff-only

    echo 'Building Docker image...'
    install
}

function run_detection {
    echo 'Removing old container...'
    sudo docker rm food-detection-embedded

    echo 'Creating container...'
    if [[ "$1" -eq 1 ]]; then
        echo 'Running in focus/dry mode...'
        arg="--dry"
    fi
    echo 'Running detections....'
    sudo docker run --name food-detection-embedded --privileged -v "$dir_absolute/archive_detection_images:/app/archive_detection_images" -v "$dir_absolute/archive_check_focus_images:/app/archive_check_focus_images" -v "$dir_absolute/logs:/app/logs" food-detection-embedded $2 $arg
}

function install {
    mkdir -p archive_detection_images
    mkdir -p archive_check_focus_images
    mkdir -p logs

    echo 'Building Docker image...'
    sudo docker build -t food-detection-embedded .
}

if [ "${command_arg}" == "install" ]; then
    install
    echo ''
    echo 'Done. Now use `./food_detector.sh detect` to detect some foods!'

elif [ "${command_arg}" == "install_prod" ]; then
    install
    # TODO: setup services

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
    run_detection 1

elif [ "${command_arg}" == "clean" ]; then
    echo 'This will delete all files and code in the repo (but copy archive files). Are you sure you want to proceed? (y/n)'
    read decision
    echo ''
    if [ "${decision}" == "yes" ] || [ "${decision}" == "y" ]; then
        cd ..
        cp -r ./food-detection-embedded/archive_detection_images ./archive_detection_images
        cp -r ./food-detection-embedded/archive_check_focus_images ./archive_check_focus_images
        rm -rf ./food-detection-embedded
        echo 'All files removed.'
    else
        echo 'No files removed.'
    fi
else
    echo "$command_arg not recognized as a command."
    echo 'Please use: `detect`, `focus`, `pull`, `pull+detect`, `clean`, `install_prod`, or `install`.'
fi
