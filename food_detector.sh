#!/usr/bin/env bash

dir="$(dirname "$0")"
dir_absolute="$(readlink -m "$dir")"
cd "$dir"

command_arg=$1
additional_args=$2

function pull_changes {
    echo 'Pulling changes from GitHub...'
    git pull --ff-only
    git submodule update --init --recursive

    echo 'Installing and setting up environment'
    install
}

function run_detection {
    # replace
}

# Checks dependencies for HX711 library
function check_dependencies {
    echo 'Checking for dependencies'
    # replace
}

function install {
    # replace
}

if [ "${command_arg}" == "install" ]; then
    install
    echo ''
    echo 'Done. Now use `./food_detector.sh detect` to detect some foods!'

elif [ "${command_arg}" == "install_prod" ]; then
    install
    # replace
    echo ''
    echo 'Done. Now the service will run on boot.'

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
    # replace
    run_detection --dry $2

elif [ "${command_arg}" == "clean" ]; then
    echo 'This will delete all files and code in the repo (but copy archive files). Are you sure you want to proceed? (y/n)'
    read decision
    echo ''
    if [ "${decision}" == "yes" ] || [ "${decision}" == "y" ]; then
        echo 'All files removed.'
    else
        echo 'No files removed.'
    fi
else
    echo "$command_arg not recognized as a command."
    echo 'Please use: `detect`, `focus`, `pull`, `pull+detect`, `clean`, `install_prod`, or `install`.'
fi
