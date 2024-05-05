import json
import logging
import os
import sys
import uuid
from time import time

import httpx

TWO_HOURS_SECONDS = 7200
# TWO_HOURS_SECONDS = 20


class TimeHelper:
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


class Logging:
    """
    Configure logging format and output type based on arguments passed to the program

    :param path: The current file path of the module creating our logging module
    :param verbose: Determines wether or not we should be printing all of the info messages or just warning and higher
    """

    def __init__(self, verbose=True):
        FORMAT = "%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s"

        loggingLevel = logging.INFO
        if not verbose:
            loggingLevel = logging.WARNING

        # Check if we want to specify an output file for the logging
        if len(sys.argv) < 2:
            logging.basicConfig(format=FORMAT, level=loggingLevel)
            logging.info(
                "No output file specified file logging will be disabled to enable: ./main.py <outputfilepath>"
            )
        else:
            logging.basicConfig(
                format=FORMAT,
                level=logging.INFO,
                handlers=[logging.FileHandler(sys.argv[1]), logging.StreamHandler()],
            )


"""
Load sensor calibration details from a given file 
"""


class CalibrationLoader:
    """
    Create a new instance of our calibration data loader

    :param file: The name of the JSON file our calibration data is stored in
    """

    def __init__(self, file="CalibrationDetails.json"):
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


class RequestHandler:
    def __init__(self, dataDir="../data", secret_file="config.secret"):
        self.secret_file = secret_file
        self.dataDir = dataDir
        self.apiKey, self.endpoint, self.port = self.loadFastAPICredentials(secret_file)
        self.endpoint = f"http://{self.endpoint}:{self.port}"

    """
    Get the currently set API key
    """
    def getAPIKey(self):
        return self.apiKey

    """
    Upload the most recent files in the 'data' folder to our remote server for storage

    :return: Dictionary of base file names (ie. "colorImage") mapped to the stored location in our S3 bucket
    """
    def uploadFiles(self, fileNames: dict):
        endpoint = self.endpoint + "/api/upload_files"

        # Format request headers
        headers = {"token": self.apiKey}

        filesToUpload = {
            "colorImageFile": (
                "colorImage.jpg",
                open(fileNames["colorImage"], "rb"),
                "image/jpg",
            ),
            "depthImageFile": (
                "depthImage.jpg",
                open(fileNames["depthImage"], "rb"),
                "image/jpg",
            ),
            "heatmapImageFile": (
                "heatmap.jpg",
                open(fileNames["heatmapImage"], "rb"),
                "image/jpg",
            ),
            "topologyMapFile": (
                "depth.ply",
                open(fileNames["topologyMap"], "rb"),
                "application/octet-stream",
            ),
            "voiceRecordingFile": (
                "downsampledAudio.wav",
                open(fileNames["voiceRecording"], "rb"),
                "audio/wav",
            ),
        }

        params = {"deviceID": int(uuid.getnode())}

        client = httpx.Client()
        try:
            response = client.post(
                endpoint, params=params, headers=headers, files=filesToUpload
            ).json()
        except Exception as e:
            logging.error(f"Exception occurred while sending hearbeat: {e}")
            response = {"status": False}
            client.close()
        finally:
            client.close()

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

    def sendHeartbeat(self):
        endpoint = self.endpoint + "/api/health/heartbeat"
        client = httpx.Client()
       
        # Attempt to send the packet
        failed = False
        try:
            response = client.get(endpoint).json()
        except Exception as e:
            logging.error(f"Exception occurred while sending hearbeat: {e}")
            return False
            client.close()
        finally:
            client.close()
        

        if "is_alive" in response and response["is_alive"] == True:
            logging.info("Succsessfully recieved hearbeat!")
            return True
        else:
            logging.error("Failed to recieive heartbeat from server!")
            return False

    """
    Request that the API credentials be updated to the most recent ones stored in the file
    """

    def updateAPICreds(self):
        self.apiKey, self.endpoint, self.port = self.loadFastAPICredentials(
            self.secret_file
        )
        self.endpoint = f"http://{self.endpoint}:{self.port}"

    """
    Send a secure heartbeat request to the API
    """

    def sendSecureHeartbeat(self):
        endpoint = self.endpoint + "/api/health/secure_heartbeat"
        headers = {
            "token": self.apiKey,
        }
        client = httpx.Client()
        try:
            response = client.get(endpoint, headers=headers).json()
        except Exception as e:
            logging.error(f"Exception occurred while sending hearbeat: {e}")
            client.close()
            return False
        finally:
            client.close()

        if "is_alive" in response and response["is_alive"] == True:
            logging.info("Succsessfully recieved hearbeat!")
            return True
        else:
            logging.error("Failed to recieive heartbeat from server!")
            return False

    """
    Send a request to our API endpoint, this includes our file upload procedure

    :param data: The complete JSON data packet 
    """

    def sendAPIRequest(self, fileNames: dict, data: dict):
        endpoint = self.endpoint + "/api/scan"
        fileLocations = self.uploadFiles(fileNames)

        if len(fileLocations) > 0:

            # API Request
            headers = {
                "token": self.apiKey,
            }

            payload = {
                "colorImage": str(fileLocations["colorImage"]),
                "depthImage": str(fileLocations["depthImage"]),
                "heatmapImage": str(fileLocations["heatmapImage"]),
                "topologyMap": str(fileLocations["topologyMap"]),
                #"segmentImage": str(fileLocations["segmentImage"]),
                #"segmentResults": str(fileLocations["segmentResults"]),
                "voiceRecording": str(fileLocations["voiceRecording"]),
                "total_weight": float(data["NAU7802"]["data"]["weight"]),
                "weight_delta": float(data["NAU7802"]["data"]["weight_delta"]),
                "temperature": float(data["BME688"]["data"]["temperature(c)"]),
                "pressure": float(data["BME688"]["data"]["pressure(kpa)"]),
                "humidity": float(data["BME688"]["data"]["humidity(%rh)"]),
                "iaq": float(data["BME688"]["data"]["iaq"]),
                "co2_eq": float(data["BME688"]["data"]["CO2-eq"]),
                "tvoc": float(data["BME688"]["data"]["bVOC-eq"]),
                "transcription": str(
                    data["SoundController"]["data"]["TranscribedText"]
                ),
                "userTrigger": bool(data["DriverManager"]["data"]["userTrigger"]),
                "deviceID": int(uuid.getnode()),
            }

            logging.info("Sending API Request...")
            client = httpx.Client()
            try:
                response = client.post(endpoint, headers=headers, json=payload, timeout=20.0).json()
            except Exception as e:
                logging.error(f"Exception occurred while sending hearbeat: {e}")
                client.close()
                return False
            finally:
                client.close()
            
            if "status" in response and response["status"] == True:
                logging.info("Data successfully uploaded!")
                return True
            else:
                logging.error("Failed to upload data to API.")
                return False
        else:
            logging.error("No file names supplied from file upload!")
            return False

    """
    Load and return our Fast API credentials

    :param file: The file our credentials are stored in
    """

    def loadFastAPICredentials(self, file):
        secretFile = open(file, "r")
        credsJson = json.load(secretFile)
        secretFile.close()
        return (
            credsJson["FASTAPI_CREDS"]["apiKey"],
            credsJson["FASTAPI_CREDS"]["endpoint"],
            credsJson["FASTAPI_CREDS"]["port"],
        )
