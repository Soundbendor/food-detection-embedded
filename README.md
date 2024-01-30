# Food Detection IoT - Jetson Nano
Intended to run on in home compost bins for the purpose of collect AI training data.

## Production - Automatically run detections on bootup

SSH or open up a terminal on the Jetson Nano and run the following commands:

#### Setup:
```bash
git clone https://github.com/Soundbendor/food-detection-embedded.git
cd food-detection-embedded
git checkout nano-refactor
./setup.sh
```

<br>

Exit the terminal, unplug the Jetson Nano, wait 10 seconds. <br>
Then, plug the Jetson Nano back in, wait 30 seconds, and the device should automatically light up to detect foods!


### Development

#### Run Detection Loop
```bash
./src/main.py
```