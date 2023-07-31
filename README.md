# food-detection-embedded

## Production - Automatically run detections on bootup

SSH or open up a terminal on the Jetson Nano and run the following commands:

1. `cd /home/osu/Desktop`
2. `mkdir auto-detect`
3. `cd auto-detect`
4. `wget https://raw.githubusercontent.com/Soundbendor/food-detection-embedded/main/food_detector.sh`
5. `chmod +x food_detector.sh`
6. `./food_detector.sh install`
7. add the .env file with the secrets to current directory (`auto-detect/`)
8. `crontab -e`
  - the program will ask you which text editor to use, select nano or your preferred editor.
  - then, add the following as the last line: <br>
`@reboot /bin/sleep 15 && cd /home/osu/Desktop/auto-detect/ && ./auto-detect/food_detector.sh pull+detect >> ./auto-detect/logs/auto_detect_log_$(date).txt 2>&1`

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
```

### How to run the detector:
```bash
sudo venv/bin/python src/food_waste/main.py
```
