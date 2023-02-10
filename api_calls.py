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