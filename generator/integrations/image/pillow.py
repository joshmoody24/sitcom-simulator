from PIL import Image
import random

def generate_image(path: str, width:int=720, height:int=1280):
    # Generate a random color
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    # Create a blank image with the random color
    img = Image.new('RGB', (width, height), color=color)
    img.save(path)