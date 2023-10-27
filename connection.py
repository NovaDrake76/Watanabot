import os
import requests
import facebook

app_id = os.environ.get('APP_ID')
app_secret = os.environ.get('APP_SECRET')
user_access_token = os.environ.get('USER_ACCESS_TOKEN')
page_access_token = os.environ.get('PAGE_ACCESS_TOKEN')
page_id = os.environ.get('PAGE_ID')

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
        response = graph.put_photo(image=open(output_path, 'rb'), message=text)
    elif file_type == 'mp4':
        response = True
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

        if response.status_code != 204:
            print(f"Failed to send to Discord. Status code: {response.status_code}. Response text: {response.text}")

else:
    print('Failed to upload: No page access token found')