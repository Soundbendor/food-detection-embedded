#!/usr/bin/env bash

command_arg=$1
MAIN="./src/food_waste/main.py"

function pull_changes {
    echo 'Pulling changes from GitHub...'
    git pull --ff-only

    echo 'Installing dependencies...'
    ./venv/bin/pip3 install -qr requirements.txt

    cd ..
}

function run_detection {
    echo 'Running detections....'
    echo '(press ctrl+c to stop)'
    sudo ./venv/bin/python3 $MAIN $2
}

function install {
    mkdir -p archive_detection_images
    mkdir -p archive_check_focus_images
    mkdir -p logs

    echo 'Creating virtual environment for dependencies...'
    python3 -m venv venv
    echo 'Installing dependencies (may take a minute)...'
    ./venv/bin/pip3 install -qr requirements.txt

    echo 'Copying native opencv library to virtual environment...'
    ln -s /usr/lib/python3.6/dist-packages/cv2/python-3.6/cv2*.so ./venv/lib/python3.6/site-packages/cv2.so

    cd ..
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
    sudo ./venv/bin/python3 $MAIN --dry $2

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
    echo '`${command_arg}` not recognized as a command.'
    echo 'Please use: `detect`, `focus`, `pull`, `pull+detect`, `clean`, `install_prod`, or `install`.'
fi
