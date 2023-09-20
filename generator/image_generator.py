from .integrations.image import stability, pillow
from tqdm import tqdm
from typing import List
from .models import Line

# TODO: make quality do something
def generate_images(lines: List[Line], quality=25, width=720, height=1280, global_style='', debug=True):
    counter = 1
    for line in tqdm(lines, desc="Generating images"):
        prefix = f"./tmp/{counter}_"
        if not debug:
            stability.generate_image(prompt=line.image_prompt + ', ' + global_style, prefix=str(prefix) + '_', width=width, height=height)
        else:
            pillow.generate_image(prefix + "empty.png", width, height)
        counter += 1