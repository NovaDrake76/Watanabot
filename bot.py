import json
import os
from PIL import Image, ImageDraw, ImageFont
import random

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

source_path = "gostosa"
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

    
        text = source_path.split("/")[-1].split(".")[0]
      
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


try:
    # Load the phrases from the JSON file
    with open("phrases.json", "r", encoding="UTF-8") as f:
        phrases = json.load(f)

        phrases = phrases["phrases"]


    # Choose 2 random phrases from the list
    random_phrases = random.sample(phrases, 2)


    # Create a new phrase from the 3 random phrases 
    new_phrase = f"{random_phrases[0]} {random_phrases[1]} "

    # Save the new phrase to the output folder
    with open("output/text.txt", "w") as f:
        f.write(new_phrase)
except:
    with open("output/text.txt", "w") as f:
        f.write("")
    pass



