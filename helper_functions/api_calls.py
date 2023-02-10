import os

#----- Functions to help with API calls: -----

def check_for_secrets():
    if os.getenv("PROXY_ID_NUM_LINK") is None \
        or os.getenv("API_KEY") is None \
        or os.getenv("PROXY_LOGIN") is None:
        print("Secrets could not be found in current directory. Please include them in a .env file.")
        return False
    return True


async def get_ngrok_link(httpx_client):
    print('Getting ngrok link')
    num_attepmts = 3
    for _ in range(num_attepmts):
        try:
            response = await httpx_client.get(os.getenv("PROXY_ID_NUM_LINK"))
            if response.status_code == 200:
                ngrok_url = f"https://{response.text.strip()}.ngrok.io"
                return ngrok_url
            print(f"Error in connecting to get ngrok link, status code: {response.status_code}")
        except ConnectionError as e:
            print("Connection error in getting ngrok link, retrying.")
        except BaseException as e:
            print("Exception in getting ngrok link, retrying.")
    
    print(f"Could not get ngrok link after {num_attepmts} attempts. Aborting.")
    return None


async def post_image_for_detection(remote_url, httpx_client, image_location, image_name):    
    files = {'img_file': (image_location, open(image_location, 'rb'), 'image/jpg')}
    
    print(f'Posting image to {remote_url}/api/model/detect for detection')

    apikey = os.getenv("API_KEY")
    authorization = os.getenv("PROXY_LOGIN")

    num_attempts = 3
    for i in range(num_attempts):
        try:
            request = await httpx_client.post(f'{remote_url}/api/model/detect', data = {'img_name': image_name},
                                    headers={'token': apikey, 'Authorization':authorization}, files = files, timeout=45.0)    

            print(f'API call received response: {request}')
            
            # Save the returned image to the detection archive for later reference.
            api_response_file_location = f'archive_detection_images/post_detection_{image_name}'
            
            # Create the file and write the request content to it.
            FileReturn = open(api_response_file_location, 'wb')
            FileReturn.write(request.content)
            FileReturn.close()
            return api_response_file_location
        
        except ConnectionError as e:
            print("Connection error in getting ngrok link, retrying.")
        except BaseException as e:
            print(e)
            print(f"post_image_for_detection attempt #{i + 1} failed.{' Trying again.' if i < num_attempts - 1 else ' Done retrying.'}")

    return None
