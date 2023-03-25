import json
import os
import random
from PIL import Image, ImageDraw, ImageFont

# Set the paths to the source and output images folders
source_folder = "sources/"
output_folder = "output/"

# Load the template specifications from the JSON file
with open("templates/templates.json", "r") as f:
    templates = json.load(f)

# Choose a random template from the list
template = random.choice(templates)

# Load the template image
template_path = template["template_path"]
template_image = Image.open(template_path)


# Set up the drawing context
draw = ImageDraw.Draw(template_image)

# Loop over each element in the template and add the corresponding image or text
for element in template["elements"]:
    if element["type"] == "image":
        # Choose a random source image from the folder
        source_path = os.path.join(source_folder, random.choice(os.listdir(source_folder)))

        # Load the source image
        source_image = Image.open(source_path)

        has_text = element.get("has_text", False)

        # Resize the source image to fit the template
        source_image = source_image.resize(element["size"])

        # Paste the source image onto the final image
        template_image.paste(source_image, element["position"])
    elif element["type"] == "text":
        # Set up font size
        font_size = element["font_size"]


        # Set up the text color
        text_color = element["text_color"]

        # Draw the text onto the final image
        draw.text(element["position"], source_path.split("/")[-1].split(".")[0], fill=text_color, font=ImageFont.truetype("arial.ttf", font_size))


# Save the final image
output_path = os.path.join(output_folder, "output.png")
template_image.save(output_path)
