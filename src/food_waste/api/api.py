import os
import time
from food_waste.api.exception import *
import food_waste.log as console

class ImageApi:
  """
  Used to post images to a remote server for detection.

  :param httpx_client: The httpx client to use for requests.
  :param remote_url: The URL/host of the remote server.
  :param num_attempts: The number of times to attempt a request before giving up.
  :param archive_loc_prefix: The prefix to use for the archive location of the returned image.
  :param timeout: The timeout for the request.
  """

  def __init__(
      self,
      httpx_client,
      remote_url,
      num_attempts = 3,
      archive_loc_prefix = 'archive_detection_images/post_detection_',
      timeout = 45.0
    ):
    self.client = httpx_client
    self.remote_url = remote_url
    self.num_attempts = num_attempts
    self.archive_loc_prefix = archive_loc_prefix
    self.timeout = timeout

  def get_secret():
    """
    Returns the API key from the environment.

    :returns: The API key.
    :raises MissingSecretsError: If the API key is not found in the environment.
    """
    key = os.getenv("API_KEY")
    if key is None:
      raise MissingSecretsError("Secrets could not be found in current directory. Please include them in a .env file.")
    return key

  async def post_image(self, path, name):
    """
    Posts an image to the remote server for detection.

    :param path: The path to the image to post.
    :param name: The name of the image to post.
    :returns: The path to the image returned by the server.
    :raises RequestFailedError: If the request fails.
    :raises MissingSecretsError: See :func:`get_secret`.
    """
    files = {
      "img_file": (
        path,
        open(path, "rb"),
        "image/jpg"
      )
    }

    api_key = self.get_secret()

    for i in range(self.num_attempts):
      try:
        console.debug(f"Posting image '{name}' to {self.remote_url}/api/model/detect")
        request = self.client.post(
          f"{self.remote_url}/api/model/detect",
          data = {"img_name": name},
          headers = {"token": api_key},
          files = files,
          timeout = self.timeout
        )

        console.debug(f"Archiving image '{name}' to {self.archive_loc_prefix}{name}")
        response_file_location = f"{self.archive_loc_prefix}{name}"
        response_file = open(response_file_location, "wb")
        response_file.write(request.content)
        response_file.close()
        return response_file_location
      except ConnectionError as e:
        console.error(f"Connection error occurred while posting image '{name}' to {self.remote_url}/api/model/detect", f"{i} / {self.num_attempts}", e)
      except BaseException as e:
        console.error(f"Error occurred while posting image '{name}' to {self.remote_url}/api/model/detect", f"{i} / {self.num_attempts}", e)
      time.sleep(1)
    raise RequestFailedError("The request failed. Check the logs for more information.")
