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
    def __init__(self, dataDir = "../data", secret_file="config.secret"):
        self.dataDir = dataDir
        self.apiKey, self.endpoint = self.loadFastAPICredentials(secret_file)
    
    """
    Upload the most recent files in the 'data' folder to our remote server for storage

    :return: Dictionary of base file names (ie. "colorImage") mapped to the stored location in our S3 bucket
    """
    def uploadFiles(self):
        endpoint = self.endpoint + "/api/upload_files"

        filesToUpload = {
            "colorImageFile": open(f"{self.dataDir}/colorImage.jpg", "rb"),
            "depthImageFile": open(f"{self.dataDir}/depthImage.jpg", "rb"),
            "heatmapImageFile": open(f"{self.dataDir}/heatmap.jpg", "rb"),
            "topologyMapFile": open(f"{self.dataDir}/depth.ply", "rb"),
            "voiceRecordingFile ": open(f"{self.dataDir}/downsampledAudio.wav", "rb")
            }
        
        # API Request
        headers = {
            "accept": "application/json",
            "token": self.apiKey,
            "Content-Type": "multipart/form-data"
        }

        params = {
            "deviceID": int(uuid.getnode())
        }
    
        response = requests.post(endpoint, params=params, headers=headers,files=filesToUpload).json()
        if response["status"] == True:
            del response["status"]
            # Upload files to FastAPI and return the resu
            logging.info(f"Successfully uploaded files to server!")
            return response
        else:
            logging.info(f"Failed to upload files to server!")
            return {}
    
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
        endpoint = self.endpoint + "/api/model/detect"
        # fileLocations = self.uploadFiles()
        
        # API Request
        # headers = {
        #     "accept": "application/json",
        #     "token": self.apiKey,
        #     "Content-Type": "application/json"
        # }

        image_location = "{self.dataDir}/colorImage.jpg",
        files = {'img_file': (image_location, open(image_location, 'rb'), 'image/jpg')}
        request = https_client.post(endpoint, data= {'img_name': image_name}, headers=headers, files = files, timeout=45.0)


        response = requests.post(endpoint, headers=headers, json=payload).json()
        if('status' in response and response["status"] == True):
            logging.info("Data successfully uploaded!")
        else:
            logging.error("Failed to upload data to API.")
            
        
    
    """
    Load and return our Fast API credentials

    :param file: The file our credentials are stored in
    """
    def loadFastAPICredentials(self, file):
        secretFile = open(file, 'r')
        credsJson = json.load(secretFile)
        secretFile.close()
        return (credsJson["FASTAPI_CREDS"]["apiKey"], credsJson["FASTAPI_CREDS"]["endpoint"])
