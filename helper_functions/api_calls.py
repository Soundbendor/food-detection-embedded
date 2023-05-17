import os

#----- Functions to help with API calls: -----

def check_for_secrets():
    if os.getenv("API_KEY") is None:
        print("Secrets could not be found in current directory. Please include them in a .env file.")
        return False
    return True


async def post_image_for_detection(remote_url, httpx_client, image_location, image_name):    
    files = {'img_file': (image_location, open(image_location, 'rb'), 'image/jpg')}
    
    print(f'Posting image to {remote_url}/api/model/detect for detection')

    api_key = os.getenv("API_KEY")

    num_attempts = 3
    for i in range(num_attempts):
        try:
            request = await httpx_client.post(f'{remote_url}/api/model/detect', data = {'img_name': image_name},
                                    headers={'token': api_key}, files = files, timeout=45.0)    

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
