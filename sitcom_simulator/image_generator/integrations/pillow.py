from PIL import Image
import random
import tempfile

def generate_image(width:int=720, height:int=1280):
    # Generate a random color
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    
    # Create a blank image with the random color
    img = Image.new('RGB', (width, height), color=color)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp:
        img.save(temp.name)
        return temp.name