import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import boto3
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip, TextClip
import io
import numpy as np
import requests

# Initialize the S3 client
s3 = boto3.client('s3')

session = boto3.Session(
    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
    region_name='South America (Sao Paulo)'
)

# Function to get a random image from S3
def get_random_s3_image(bucket_name, folder_name):
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f'{folder_name}/')
    all_objects = response['Contents']
    all_objects = [obj for obj in all_objects if not obj['Key'].endswith('/')]
    random_file = random.choice(all_objects)
    random_file_key = random_file['Key']
    obj = s3.get_object(Bucket=bucket_name, Key=random_file_key)
    return io.BytesIO(obj['Body'].read()), random_file_key

# Function to get a random video from a JSON file
def get_random_video():
    with open('sources/videoSources.json', 'r') as f:
        video_data = json.load(f)
    return random.choice(video_data['videos'])

composite_elements = []

# Read template specifications and choose a random template
with open('templates/templates.json', 'r') as f:
    templates = json.load(f)

template = random.choice(templates)
template_path = template["template_path"]
template_image = Image.open(template_path)
draw = ImageDraw.Draw(template_image)

has_video = False  # Flag to check if any video is used
video_used = False  # Flag to indicate if a video has already been chosen for this post

# List to collect resources that need to be closed later
resources_to_close = []

i  = 0
# Loop through each element in the template to prepare sources
for element in template["elements"]:
    element_type = element["type"]
    position = tuple(element["position"])
    size = tuple(element["size"]) if "size" in element else None

    if element_type == "image":
        use_video = False  # Initialize as False

        if not video_used:  # Only consider using a video if one hasn't been used yet
            use_video = random.random() < 0.5  # Adjust the probability as you like

        if use_video:
            print("Using video for element number", i)
            video_used = True  # Mark that a video has been used
            has_video = True
            video_data = get_random_video()
            video_url = video_data['url']
            r = requests.get(video_url, stream=True)
            r.raise_for_status()
            with open("temp_video.mp4", 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            video_clip = VideoFileClip("temp_video.mp4")
            video_clip_resized = video_clip.resize(newsize=size)
            composite_elements.append(video_clip_resized.set_position(position))
            resources_to_close.append(video_clip)  # Add to resources to be closed later

        else:
            random_image_data, random_image_key = get_random_s3_image('watanabot', 'sources')
            random_image = Image.open(random_image_data)
            random_image_resized = random_image.resize(size)
            random_image.close()

            if has_video:
                img_clip = ImageClip(np.array(random_image_resized)).set_duration(video_clip.duration)
                composite_elements.append(img_clip.set_position(position))
                img_clip.close()
            else:
                template_image.paste(random_image_resized, position)

    elif element_type == "text":
        font_size = element["font_size"]
        text_color = element["text_color"]
        font = ImageFont.truetype('arial.ttf', font_size)

        if has_video:
            text = video_data['title']
        else:
            text = random_image_key.split("/")[-1].split(".")[0]
            draw.text(element["position"], text, fill=text_color, font=font)

    elif element_type == "mandatoryImage":
        source_image = Image.open(element["source"])
        source_image_resized = source_image.resize(size)
        source_image.close()

        if has_video:
            img_clip = ImageClip(np.array(source_image_resized)).set_duration(video_clip.duration)
            composite_elements.append(img_clip.set_position(position))
            img_clip.close()
        else:
            template_image.paste(source_image_resized, position)

    i += 1

# Check if any video elements are present
if has_video:
    template_image_clip = ImageClip(template_path).set_duration(video_clip.duration)
    composite_elements.insert(0, template_image_clip)
    final_video = CompositeVideoClip(composite_elements).set_duration(video_clip.duration)
    output_path = "output/output.mp4"
    final_video.write_videofile(output_path, codec="libx264")
    output_path = "output/output.mp4"

    with open('output/type.txt', 'w') as f:
        f.write('video')

    # Close video resources
    for resource in resources_to_close:
        resource.reader.close()
        resource.audio.reader.close_proc()
else:
    output_path = "output/output.png"
    template_image.save(output_path)
    with open('output/type.txt', 'w') as f:
        f.write('image')

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
        f.write("")
    pass


# try:
  
#     payload = {
#             "content": "Boa Noite",
#     }

#     # file = {'file': open(output_path, 'rb')}

#     # Send POST request to Discord webhook
#     response = requests.post("https://discord.com/api/webhooks/1160361902304657428/_njx1u0FLUE2B3zfkNfpEQkdoe5mOSvxqL20wDuDWXc7rnETU87t7oxH_f_svxFjmBAn",
#                                   data=payload,
#                             # files=file)
#                             )
    
# except:
#         print("error in discord webhook")