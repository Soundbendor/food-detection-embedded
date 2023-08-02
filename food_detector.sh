#!/usr/bin/env bash

dir="$(dirname "$0")"
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
    echo 'Running detections....'
    echo '(press ctrl+c to stop)'
    if [ $1 == 1 ]; then
        echo 'Checking camera focus...'
        sudo docker run food-detection-embedded --dry $2
    else
        sudo docker run food-detection-embedded $2
    fi
}

function install {
    mkdir -p archive_detection_images
    mkdir -p archive_check_focus_images
    mkdir -p logs

    echo 'Building Docker image...'
    sudo docker build -t food-detection-embedded .

    echo 'Creating container...'
    sudo docker create --name food-detection-embedded --privileged -v "$dir/archive_detection_images:/app/archive_detection_images" -v "$dir/archive_check_focus_images:/app/archive_check_focus_images" -v "$dir/logs:/app/logs" food-detection-embedded
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
