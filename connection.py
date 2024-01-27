import os
import requests
import facebook
from requests_oauthlib import OAuth1Session

app_id = os.environ.get('APP_ID')
app_secret = os.environ.get('APP_SECRET')
user_access_token = os.environ.get('USER_ACCESS_TOKEN')
page_access_token = os.environ.get('PAGE_ACCESS_TOKEN')
page_id = os.environ.get('PAGE_ID')
consumer_key = os.environ.get('TWITTER_CONSUMER_KEY')
consumer_secret = os.environ.get('TWITTER_CONSUMER_SECRET')
access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')

# Create OAuth1Session instance
oauth = OAuth1Session(
    consumer_key,
    client_secret=consumer_secret,
    resource_owner_key=access_token,
    resource_owner_secret=access_token_secret
)

graph = facebook.GraphAPI(page_access_token)

session = requests.Session()
session.verify = False

# Determine whether it's an image or video based on the information written by bot.py
try:
    with open('output/type.txt', 'r') as f:
        file_type = f.read().strip()
except FileNotFoundError:
    print("Could not find 'type.txt'. Defaulting to image.")
    file_type = 'png'

output_path = f'output/output.{file_type}'

if page_access_token:
    try:
        with open('output/text.txt', 'r') as f:
            text = f.read()
    except:
        text = ""

    if file_type == 'png':
        print('Uploading image...')
        # Upload image to Facebook
        # upload_url = f"https://graph.facebook.com/v19.0/123920583940036/photos"
        # response = requests.post(
        #     upload_url,
        #     params={
        #         "access_token": page_access_token
        #     },
        #     files={
        #         "source": open(output_path, "rb")
        #     }
        # )

        # if response.status_code != 200:
        #     raise Exception(
        #         f"Image upload failed: {response.status_code} {response.text}"
        #     )

        # Uploading media to Twitter (separate endpoint for media upload)
        files = {
            'media': (output_path.split('/')[-1], open(output_path, 'rb')),
            'media_category': 'tweet_image'
        }

        # Media upload
        media_response = oauth.post(
            "https://upload.twitter.com/1.1/media/upload.json",
            files={'media': (output_path.split('/')[-1], open(output_path, 'rb'))}
        )


        if media_response.status_code != 200:
            raise Exception(
                "Media upload failed: {} {}".format(media_response.status_code, media_response.text)
            )
        media_id = media_response.json()['media_id_string']
        # Creating tweet with media
        twitter_payload = {
        "text": text,
        "media": {
            "media_ids": [media_id]
        }
        }
        twitter_response = oauth.post(
            "https://api.twitter.com/2/tweets",
            json=twitter_payload
        )
        if twitter_response.status_code != 201:
            raise Exception(
                "Tweet creation failed: {} {}".format(twitter_response.status_code, twitter_response.text)
            )
    elif file_type == 'mp4':
        response = True
    #     print('Uploading video...')        
    #     # Uploading media to Twitter (separate endpoint for media upload)
    #     files = {
    #         'media': (output_path.split('/')[-1], open(output_path, 'rb')),
    #         'media_category': 'tweet_video'
    #     }

    #     # Media upload
    #     media_response = oauth.post(
    #         "https://upload.twitter.com/1.1/media/upload.json",
    #         files={'media': (output_path.split('/')[-1], open(output_path, 'rb'))}
    #     )


    #     if media_response.status_code != 200:
    #         raise Exception(
    #             "Media upload failed: {} {}".format(media_response.status_code, media_response.text)
    #         )
    #     media_id = media_response.json()['media_id_string']
    #     # Creating tweet with media
    #     twitter_payload = {
    #     "text": text,
    #     "media": {
    #         "media_ids": [media_id]
    #     }
    #     }
    #     twitter_response = oauth.post(
    #         "https://api.twitter.com/2/tweets",
    #         json=twitter_payload
    #     )
    #     if twitter_response.status_code != 201:
    #         raise Exception(
    #             "Tweet creation failed: {} {}".format(twitter_response.status_code, twitter_response.text)
    #         )
    # else:
    #     print('Failed to upload: Invalid file type')        
        
    #     video = open(output_path, 'rb')
    #     response = graph.put_object(
    #         parent_object='me',
    #         connection_name='videos',
    #         source=video.read(),
    #         description=text
    #     )
    #     video.close()

    if response is None:
        print('Failed to upload')
        payload = {
           "content": "<@830191630069137459> erro ao postar",
        }

        # Send POST request to Discord webhook
        response = requests.post("https://discord.com/api/webhooks/1160361902304657428/_njx1u0FLUE2B3zfkNfpEQkdoe5mOSvxqL20wDuDWXc7rnETU87t7oxH_f_svxFjmBAn",
                                data=payload)
    else:
        print('Uploaded successfully')

        payload = {
            "content": "New post: " + text,
        }
        file = {
            "file": (output_path.split('/')[-1], open(output_path, 'rb'))
        }
        response = requests.post(
            "https://discord.com/api/webhooks/1160361902304657428/_njx1u0FLUE2B3zfkNfpEQkdoe5mOSvxqL20wDuDWXc7rnETU87t7oxH_f_svxFjmBAn",
            data=payload,
            files=file
        )

else:
    print('Failed to upload: No page access token found')