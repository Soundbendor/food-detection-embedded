import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore",category=DeprecationWarning)
    import boto3

import logging
import sys
import os
import json
from time import time, gmtime, strftime

import glob
import uuid
import requests


TWO_HOURS_SECONDS = 7200
#TWO_HOURS_SECONDS = 20

class TimeHelper():
    def __init__(self):
        self.lastTime = time()
    
    """
    Check to see if we have reached the two hour interval and should trigger the collection

    :return A bool representing if our 2 hour interval is up
    """
    def twoHourInterval(self) -> bool:
        currentTime = int(time())
        if (currentTime % TWO_HOURS_SECONDS) == 0 and currentTime != self.lastTime:
            self.lastTime = currentTime
            return True
        return False

"""
General wrapper for initializing logging formats and file storage
"""
class Logging():
    """
    Configure logging format and output type based on arguments passed to the program

    :param path: The current file path of the module creating our logging module
    :param verbose: Determines wether or not we should be printing all of the info messages or just warning and higher
    """
    def __init__(self, path, verbose=True):
        FORMAT = '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s'

        loggingLevel = logging.INFO
        if not verbose:
            loggingLevel = logging.WARNING

        # Check if we want to specify an output file for the logging
        if(len(sys.argv) < 2):
            logging.basicConfig(format=FORMAT, level=loggingLevel)
            logging.info("No output file specified file logging will be disabled to enable: ./main.py <outputfilepath>")
        else:
            logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.FileHandler(str(os.path.dirname(os.path.abspath(path))) + "/" + sys.argv[1]), logging.StreamHandler()])

"""
Load sensor calibration details from a given file 
"""
class CalibrationLoader():

    """
    Create a new instance of our calibration data loader

    :param file: The name of the JSON file our calibration data is stored in
    """
    def __init__(self, file = "CalibrationDetails.json"):
        logging.info(f"Retrieving calibration details from file: {file}")

        # Attempt to open the file and convert the contents to JSON object
        with open(file, "r") as f:
            self.data = json.load(f)
            logging.info("Succsessfully loaded calibration details!")
    
    """
    Retrieve the given calibration data

    :param field: The key name where the calibration data is stored
    """
    def get(self, field):
        return self.data[field]
    
"""
Handles requests to remote APIs (S3 and FastAPI)
"""
class RequestHandler():
    def __init__(self, secret_file="config.secret"):
        self.awsCreds = self.loadAWSCredentials(secret_file)
        self.apiKey, self.endpoint = self.loadFastAPICredentials(secret_file)
        self.s3 = boto3.client("s3", aws_access_key_id=self.awsCreds[0], aws_secret_access_key=self.awsCreds[1], region_name=self.awsCreds[2])
    
    """
    Upload the most recent files in the 'data' folder to S3

    :return: Dictionary of base file names (ie. "colorImage") mapped to the stored location in our S3 bucket
    """
    def uploadS3(self):
        dataFiles = glob.glob("../data/*")
        currentTime = time()
        imageLocations = {
            "colorImage": "",
            "depthImage": "",
            "depth": "",
            "downsampledAudio": "",
            "heatmap": ""
        }
        
        # Glob files in data folder and format new names with timestamp upload to S3 then update the upload URL for the correspoding file in the dictionary
        for file in dataFiles:

            # Format new file name with date for upload to S3
            fileSplit = file.split("/")
            file_name = fileSplit[len(fileSplit)-1].split(".")
            
            # File formatted as fileType_Data_UUID.filextension
            # eg. colorImage_2024-1-29--22-14-23_233349935970430
            formattedName = strftime(f"{file_name[0]}_%Y-%m-%d--%H-%M-%S_{uuid.getnode()}.{file_name[1]}",gmtime(currentTime))

            # Upload the file itself with the new name to S3
            self.s3.upload_file(file, self.awsCreds[3], formattedName)
            
            # Create the URL where this file will now be located at
            uploadUrl = f"https://{self.awsCreds[3]}.s3.{self.awsCreds[2]}.amazonaws.com/{formattedName}"

            # Set the URL to the matching file in the dictionary
            imageLocations[file_name[0]] = uploadUrl
            logging.info(f"Successfully uploaded {formattedName} to S3!")
            
        
        return imageLocations
    
    """
    Test method to verify our API key is functioning

    :param apiKey: Our API Key used to authenticate with our API
    """
    def sendSecureHeartbeat(self):
        endpoint = self.endpoint + "/api/health/secure_heartbeat"
        response = requests.get(
            endpoint, 
            headers={
                "accept": "application/json",
                "token": self.apiKey
            }
        )
        print(response.json())
        # TODO: Return true or false depedning on return state


    """
    Send a request to our API endpoint 

    :param data: The complete JSON data packet 
    """
    def sendAPIRequest(self, data: dict):
        endpoint = self.endpoint + "/api/scan"
        s3Locations = self.uploadS3()
        
        # API Request
        headers = {
            "accept": "application/json",
            "token": self.apiKey,
            "Content-Type": "application/json"
        }

        payload = {
            "colorImage": str(s3Locations["colorImage"]),
            "depthImage": str(s3Locations["depthImage"]),
            "heatmapImage": str(s3Locations["heatmap"]),
            "topologyMap": str(s3Locations["depth"]),
            "voiceRecording": str(s3Locations["downsampledAudio"]),
            "total_weight": float(data["NAU7802"]["data"]["weight"]),
            "weight_delta": float(data["NAU7802"]["data"]["weight_delta"]),
            "temperature": float(data["BME688"]["data"]["temperature(c)"]),
            "pressure": float(data["BME688"]["data"]["pressure(kpa)"]),
            "humidity": float(data["BME688"]["data"]["humidity(%rh)"]),
            "iaq": float(data["BME688"]["data"]["iaq"]),
            "co2_eq": float(data["BME688"]["data"]["CO2-eq"]),
            "tvoc": float(data["BME688"]["data"]["bVOC-eq"]),
            "transcription": str(data["SoundController"]["data"]["TranscribedText"]),
            "userTrigger": bool(data["DriverManager"]["data"]["userTrigger"])
        }

        response = requests.post(endpoint, headers=headers, json=payload).json()
        if('status' in response and response["status"] == True):
            logging.info("Data successfully uploaded!")
        else:
            logging.error("Failed to upload data to API.")
            
        

    """
    Load our AWS secret credentials in from a file

    :param file: The file in which the credentials are stored
    """
    def loadAWSCredentials(self, file):
        secretFile = open(file, 'r')
        credsJson = json.load(secretFile)
        secretFile.close()
        return (credsJson["AWS_CREDS"]["access_key_id"], credsJson["AWS_CREDS"]["access_key"], credsJson["AWS_CREDS"]["region"], credsJson["AWS_CREDS"]["bucket"])
    
    """
    Load and return our Fast API credentials

    :param file: The file our credentials are stored in
    """
    def loadFastAPICredentials(self, file):
        secretFile = open(file, 'r')
        credsJson = json.load(secretFile)
        secretFile.close()
        return (credsJson["FASTAPI_CREDS"]["apiKey"], credsJson["FASTAPI_CREDS"]["endpoint"])
