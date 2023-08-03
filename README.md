# food-detection-embedded

## Production - Automatically run detections on bootup

SSH or open up a terminal on the Jetson Nano and run the following commands:

```bash
cd /home/osu/Desktop
git clone https://github.com/Soundbendor/food-detection-embedded.git
cd food-detection-embedded
./food_detector.sh install_prod
```

<br>

Exit the terminal, unplug the Jetson Nano, wait 10 seconds. <br>
Then, plug the Jetson Nano back in, wait 30 seconds, and the device should automatically light up to detect foods!

<br>

Note: do not unplug the Jetson Nano while the detection script is running, this could damage the sensors. Instead: <br>
**To stop the detection script**: Hold the tare/power button for around 5-6 seconds, until the lights turn off. <br>

<br>

## Development

### Setup:
```bash
./food_detector.sh install
```

### How to run the detector:
```bash
# One of the following:
./food_detector.sh detect
./food_detector.sh focus
```
