import os
import requests
import facebook
from PIL import Image

# set the path to the environment variables file and load it
env_path = os.path.join(os.path.dirname(__file__), '.env')


# Load the environment variables
# with open(env_path, 'r') as f:
#     for line in f:
#         key, value = line.strip().split('=')
#         os.environ[key] = value

#https://developers.facebook.com/tools/explorer?method=GET&path=me%3Ffields%3Did%2Cname&version=v16.0


# Get the Facebook API credentials
app_id = os.environ.get('APP_ID')
app_secret = os.environ.get('APP_SECRET')
user_access_token = os.environ.get('USER_ACCESS_TOKEN')
page_access_token = os.environ.get('PAGE_ACCESS_TOKEN')
page_id = os.environ.get('PAGE_ID')

graph = facebook.GraphAPI(page_access_token)


# Obtain a Page Access Token for the page
# graph = facebook.GraphAPI(access_token='user_access_token', version='3.1')
# page_access_token = graph.get_app_access_token('161493586812298', app_secret)


# Create a Facebook session
session = requests.Session()
session.verify = False  # Disable SSL verification for simplicity

# Upload the image to Facebook
if (page_access_token != None):

    # Upload the image to Facebook
    response = graph.put_photo(image=open('output/output.png', 'rb'), message='Flamengo')

   
    if 'error' in response:
        print(f'Failed to upload image: {response["error"]["message"]}')
    else:
        print('Image uploaded successfully')

else:
    print('Failed to upload image: No page access token found')
