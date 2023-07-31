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
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# To link the built-in opencv library to the virtual environment
ln -s /usr/lib/python3.6/dist-packages/cv2/python-3.6/cv2*.so ./venv/lib/python3.6/site-packages/cv2.so
```

or

```bash
./food_detector.sh install
```

### How to run the detector:
```bash
sudo venv/bin/python src/food_waste/main.py
```
