from PIL import Image
import random

def generate_image(path: str):
    # Generate a random color
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    # Create a blank image with the random color
    img = Image.new('RGB', (16, 16), color=color)
    img.save(path)