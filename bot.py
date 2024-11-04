import io
import json
import os
import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import boto3
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.audio.AudioClip import AudioArrayClip
import sys
from datetime import datetime

import requests

# Initialize the S3 client
s3 = boto3.client('s3')

session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='South America (Sao Paulo)'
)

# Function to get a random image from S3. 60% of chance to get a "new" image, where "new" means that its one of the last 40 images uploaded
def get_random_s3_image(bucket_name, folder_name):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f'{folder_name}/')
    all_objects = response['Contents']
    all_objects = [obj for obj in all_objects if not obj['Key'].endswith('/')]

    # Sort objects by LastModified date
    all_objects.sort(key=lambda obj: obj['LastModified'], reverse=True)

    # Get the last 40 images
    new_images = all_objects[:40]

    # Decide whether to pick a "new" image or a random image
    if random.random() < 0:  # 0% chance
        selected_image = random.choice(new_images)
    else:
        selected_image = random.choice(all_objects)

    selected_image_key = selected_image['Key']
    obj = s3.get_object(Bucket=bucket_name, Key=selected_image_key)
    return io.BytesIO(obj['Body'].read()), selected_image_key

# Function to get a random video from a JSON file
def get_random_video():
    with open('sources/videoSources.json', 'r') as f:
        video_data = json.load(f)
    return random.choice(video_data['videos'])

composite_elements = []
has_video = False  # Flag to check if any video is used
video_duration = None  # Store the duration of the video

try:
    # Load the phrases from the JSON file
    with open("phrases.json", "r", encoding="utf-8") as f:  # Add encoding here
        phrases = json.load(f)
        phrases = phrases["phrases"]
    random_phrases = random.sample(phrases, 2)
    new_phrase = random_phrases[0] + " " + random_phrases[1]
    with open("output/text.txt", "w", encoding="utf-8") as f:  # Add encoding here
        f.write(new_phrase)
except Exception as e:
    print("error in text generation: " + str(e))
    with open("output/text.txt", "w") as f:
        f.write("")

# Read template specifications and choose a random template
with open('templates/templates.json', 'r') as f:
    templates = json.load(f)

template = random.choice(templates)
template_path = template["template_path"]
template_image = Image.open(template_path)
draw = ImageDraw.Draw(template_image)

textArr = []
counter = 0

# Loop through each element in the template to prepare sources
for element in template["elements"]:
    element_type = element["type"]
    position = tuple(element["position"])
    size = tuple(element["size"]) if "size" in element else None

    if element_type == "image":
        use_video = random.random() < 0.0   # Adjust the probability as you like

        if use_video and not has_video:
            try:
                has_video = True
                video_data = get_random_video()
                video_url = video_data['url']
                r = requests.get(video_url, stream=True)
                r.raise_for_status()
                with open("temp_video.mp4", 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                video_clip = VideoFileClip("temp_video.mp4").resize(newsize=size)
                video_duration = video_clip.duration
                composite_elements.append(video_clip.set_position(position))
                textArr.append(video_data['title'])
            except Exception as e:
                print('Failed to upload video')
                payload = {
                   "content": "<@830191630069137459> erro ao postar vídeo",
                }
                # Send POST request to Discord webhook
                response = requests.post("https://discord.com/api/webhooks/1160361902304657428/_njx1u0FLUE2B3zfkNfpEQkdoe5mOSvxqL20wDuDWXc7rnETU87t7oxH_f_svxFjmBAn",
                                        data=payload)
                sys.exit()
             
        else:
            image_data, image_key = get_random_s3_image('watanabot', 'sources')
            image = Image.open(image_data).resize(size)
            img_array = np.array(image)
            img_clip = ImageClip(img_array, duration=video_duration).set_position(position)
            composite_elements.append(img_clip)
            textArr.append(image_key.split("/")[-1].split(".")[0])

    elif element_type == "text":
        try:
            font_size = element["font_size"]
            text_color = element["text_color"]
            font = ImageFont.truetype('arial.ttf', font_size)
            text = textArr[counter]
            counter += 1
            
            draw.text(position, text, fill=text_color, font=font)
        except Exception as e:
            print("error in text generation: " + str(e))
            

    elif element_type == "mandatoryImage":
        source_image = Image.open(element["source"])
        source_image_resized = source_image.resize(size)
        source_img_array = np.array(source_image_resized)
        source_img_clip = ImageClip(source_img_array, duration=video_duration).set_position(position)
        composite_elements.append(source_img_clip)
        source_image.close()

    

# Add template image to composite elements
img_array = np.array(template_image)
img_clip = ImageClip(img_array, duration=video_duration)
composite_elements.insert(0, img_clip)

# Generate final output based on composite_elements
if has_video:
    try:
        with open("output/type.txt", "w") as f:
            f.write("mp4")

        final_video = CompositeVideoClip(composite_elements)

        final_video.write_videofile(
            "output/output.mp4",
            codec="libx264",
        )
    except Exception as e:
        print("error in video generation: " + str(e))
        with open("output/type.txt", "w") as f:
            f.write("error")

else:
    final_image = CompositeVideoClip(composite_elements).set_duration(1)
    final_image.save_frame("output/output.png", t=0)
    with open("output/type.txt", "w") as f:
        f.write("png")

template_image.close()

try:
    # Load the phrases from the JSON file
    with open("phrases.json", "r", encoding="UTF-8") as f:
        phrases = json.load(f)

        phrases = phrases["phrases"]

    # Choose 2 random phrases from the list
    random_phrases = random.sample(phrases, 2)

    # Create a new phrase from flushing the 2 random phrases together and shuffling some words
    new_phrase = random_phrases[0] + " " + random_phrases[1]

    with open("output/text.txt", "w") as f:
        f.write(new_phrase)


except Exception as e:
    print("error in text generation 2" + str(e))
    with open("output/text.txt", "w") as f:
        f.write("erro ao gerar texto lmao")
    pass


# try:
  
#     payload = {
#             "content": "",
#     }

#     # file = {'file': open(output_path, 'rb')}

#     # Send POST request to Discord webhook
#     response = requests.post("https://discord.com/api/webhooks/1160361902304657428/_njx1u0FLUE2B3zfkNfpEQkdoe5mOSvxqL20wDuDWXc7rnETU87t7oxH_f_svxFjmBAn",
#                                   data=payload,
#                             # files=file)
#                             )
    
# except:
#         print("error in discord webhook")

