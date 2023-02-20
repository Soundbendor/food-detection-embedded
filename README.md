# food-detection-embedded

## Production - Automatically run detections on bootup

SSH or open up a terminal on the raspberry pi and run the following commands:

1. `cd /home/pi/Desktop`
2. `mkdir auto-detect`
3. `cd auto-detect`
4. `wget https://raw.githubusercontent.com/Soundbendor/food-detection-embedded/main/food_detector.sh`
5. `chmod +x food_detector.sh`
6. `./food_detector.sh install`
7. add the .env file with the secrets to current directory (`auto-detect/`)
8. `crontab -e` and add the following as the last line: <br>
`@reboot /bin/sleep 15 && cd /home/pi/Desktop/auto-detect/ && /home/pi/Desktop/auto-detect/food_detector.sh pull+detect >> /home/pi/Desktop/auto-detect/logs/auto_detect_log_$(date).txt 2>&1`

<br>

Exit the terminal, unplug the raspberry pi, wait 10 seconds. <br>
Then, plug the raspberry pi back in, wait 30 seconds, and the pi should automatically light up to detect foods!


<br>

## Development

### Setup:
```
$ python3 -m venv venv

$ source venv/bin/activate

$ pip install -r requirements.txt
```

### How to run the detector:
```
$ sudo venv/bin/python detect_foods.py
```
