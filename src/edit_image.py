from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os

def write_timestamp(image_path:str):

    path = os.path.expanduser(image_path)
    original_image = Image.open(path)

    # Get the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Create a drawing object
    draw = ImageDraw.Draw(original_image)

    # Set the font and size for the timestamp
    font = ImageFont.load_default()  # You can also use a specific font file and size

    # Set the position for the timestamp (bottom right corner)
    xy1,xy2,yx1,yx2 = draw.textbbox((0,0),text=timestamp, font=font)
    image_width, image_height = original_image.size
    position = (image_width - (xy2-xy1) - 10, image_height - (yx2-yx1) - 10)

    # Set the color for the timestamp (you can customize this)
    text_color = (0,0,0)

    # Add the timestamp to the image
    draw.text(position, timestamp, font=font, fill=text_color)

    # Save the modified image
    output_path = image_path.replace('.jpg', '_timestamp.jpg')
    original_image.save(os.path.expanduser(output_path))

    # Display the modified image
    original_image.show()
