#!/usr/bin/env bash

dir="$(dirname "$0")"
dir_absolute="$(readlink -m "$dir")"
cd "$dir"

command_arg=$1
additional_args=$2
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
        echo 'Using focus/dry mode...'
        arg="-d food-detection-embedded --dry $additional_args"
    elif [[ "$1" -eq 2 ]]; then
        arg="-it --entrypoint /bin/bash food-detection-embedded"
    else
        arg="-d food-detection-embedded $additional_args"
    fi

    cv2_py_loc=/usr/lib/python3.6/dist-packages/cv2
    cv2_py_out=/app/venv/lib/python3.6/site-packages/cv2
    cv2_lib_loc=/usr/lib/aarch64-linux-gnu/
    cv2_lib_out=/usr/local/host/
    
    volumes="-v \"$dir_absolute/archive_detection_images:/app/archive_detection_images\" \
        -v \"$dir_absolute/archive_check_focus_images:/app/archive_check_focus_images\" \
        -v /tmp/argus_socket:/tmp/argus_socket \
        -v /tmp:/tmp \
        -v /lib/modules:/lib/modules \
        -v $cv2_py_loc:$cv2_py_out \
        -v $cv2_lib_loc:$cv2_lib_out"
    devices="--device=/dev/video0 --device=/dev/video1"
    privileges="--network host --ipc=host --privileged --cap-add SYS_RAWIO --cap-add SYS_PTRACE --runtime nvidia"
    final_cmd="sudo docker run --name food-detection-embedded $privileges $devices $volumes $arg"

    echo "Preparing detections..."
    eval "$final_cmd"
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

elif [ "${command_arg}" == "debug" ]; then
    echo 'Removing old container...'
    sudo docker rm food-detection-embedded

    echo 'Running debug container...'
    run_detection 2

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
