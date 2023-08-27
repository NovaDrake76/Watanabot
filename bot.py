import json
import os
import io
from PIL import Image, ImageDraw, ImageFont
import random
import boto3

# Initialize S3 client
s3 = boto3.client('s3')

def get_random_s3_image(bucket_name, folder_name):
    # List all objects in a specific folder within the bucket
    response = s3.list_objects_v2(Bucket=bucket_name, Prefix=f'{folder_name}/')
    all_objects = response['Contents']

    # Remove the folder itself from the list (it is also considered an 'object' in S3)
    all_objects = [obj for obj in all_objects if not obj['Key'].endswith('/')]
    
    # Randomly select an object (file)
    random_file = random.choice(all_objects)
    random_file_key = random_file['Key']

    # Download the object to memory
    obj = s3.get_object(Bucket=bucket_name, Key=random_file_key)
    return io.BytesIO(obj['Body'].read()), random_file_key  # return both the BytesIO object and the file key


# Your existing paths and setup
source_folder = "sources/"
output_folder = "output/"

# Load the template specifications from the JSON file
with open("templates/templates.json", "r") as f:
    templates = json.load(f)

template = random.choice(templates)
template_path = template["template_path"]
template_image = Image.open(template_path)

draw = ImageDraw.Draw(template_image)

# Loop over each element in the template
for element in template["elements"]:
    if element["type"] == "image":
        # Get a random source image from S3 bucket
        source_image_stream, random_file_key = get_random_s3_image('watanabot', 'sources')
        source_image = Image.open(source_image_stream)
        
        # Resize and place the source image
        source_image = source_image.resize(element["size"])
        template_image.paste(source_image, element["position"])

    elif element["type"] == "text":
        # Set up font size
        font_size = element["font_size"]

        # Set up the text color
        text_color = element["text_color"]

        text = random_file_key.split("/")[-1].split(".")[0]
        # Draw the text onto the final image

        font = ImageFont.truetype(r'arial.ttf', font_size)
        draw.text(element["position"], text, fill=text_color, font=font)

    elif element["type"] == "mandatoryImage":
        # Load the source image
        source_image = Image.open(element["source"])

        # Resize the source image to fit the template
        source_image = source_image.resize(element["size"])

        # remove black background, make the background transparent andPaste the source image onto the final image
        template_image.paste(source_image, element["position"], source_image)

# Save the final image
output_path = os.path.join(output_folder, "output.png")
template_image.save(output_path)

# openai.api_key = os.environ.get('OPENAI_API_KEY')

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
