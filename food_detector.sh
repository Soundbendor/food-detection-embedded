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

    echo 'Installing and setting up environment'
    install
}

function run_detection {
    sudo "$dir_absolute/venv/bin/python" "$dir_absolute/src/main.py" $1 $2
}

function check_dependencies {
    ldconfig -p | grep libgpiod
    if [ $? -ne 0 ]; then
        echo 'libgpiod not found. Installing...'
        sudo apt-get install autoconf-archive
        git clone git://git.kernel.org/pub/scm/libs/libgpiod/libgpiod.git /tmp/libgpiod
        cd /tmp/libgpiod
        git checkout v1.6.3 -b v1.6.3
        ./autogen.sh --enable-tools=yes --prefix=/usr/local --enable-bindings-python
        make
        sudo make install
        rm -rf /tmp/libgpiod
    fi
}

function install {
    tmp_env_loc='/tmp/food-detection-embedded-env/'
    cv2_lib='/usr/lib/python3.6/dist-packages/cv2'

    echo 'Creating directories'
    mkdir -p archive_detection_images
    mkdir -p archive_check_focus_images
    mkdir -p logs

    echo 'Building Docker builder image...'
    sudo docker build -t food-detection-builder .

    mkdir -p $tmp_env_loc
    echo 'Executing builder...'
    sudo docker run --rm --name food-detection-builder \
        -v $tmp_env_loc:/out/ \
        food-detection-builder

    echo 'Copying virtual environment'
    echo 'Removing current environment'
    rm -rf "$dir_absolute/venv"
    sleep 1

    echo 'Generating environment'
    python3 -m venv "$dir_absolute/venv"

    echo 'Copying files from built environment'
    rsync -aq --progress "$tmp_env_loc/venv/" "$dir_absolute/venv" --exclude bin

    echo 'Removing temporary files'
    sudo rm -rf "$tmp_env_loc"

    echo 'Copying native libraries'
    cp -r $cv2_lib "$dir_absolute/venv/lib/python3.6/site-packages"
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
    run_detection $2

elif [ "${command_arg}" == "focus" ]; then
    echo 'Checking camera focus...'
    run_detection --dry $2

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
