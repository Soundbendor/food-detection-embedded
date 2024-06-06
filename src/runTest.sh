#!/bin/bash
# Created to easily run QA tests for different pieces of the system

case $1 in 

    all)
        echo "Use Ctrl + C to move on to the next test"
        echo "Testing NAU7802..."
        python3 -m tests.nauTest

        echo "Testing Realsense Depth Camera..."
        python3 -m tests.realsenseTestLeds

        echo "Testing LEDs..."
        python3 -m tests.ledTest

        echo "Testing Lid Switch..."
        python3 -m tests.lidSwitchTest

        echo "Testing MLX..."
        python3 -m tests.mlxTest

        echo "Testing BME..."
        python3 -m tests.bmeTest
        
        echo "Testing speaker and microphone..."
        python3 -m tests.soundTest
        ;;
    realsense)
        python3 -m tests.realsenseTestLeds
        ;;
    nau)
        python3 -m tests.nauTest
        ;;
    led)
        python3 -m tests.ledTest
        ;;
    switch)
        python3 -m tests.lidSwitchTest
        ;;
    mlx)
        python3 -m tests.mlxTest
        ;;
    bme)
        python3 -m tests.bmeTest
        ;;
    sound)
        python3 -m tests.soundTest
        ;;
esac