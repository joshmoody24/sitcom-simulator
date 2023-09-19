from .integrations.image import stability
from tqdm import tqdm
from typing import List
from .models import Line

def generate_image(line: Line, prefix: str, width=1024, height=1024, global_style=''):
    stability.generate_image(prompt=line.image_prompt + ', ' + global_style, prefix=str(prefix) + '_', width=width, height=height)


# TODO: make quality do something
def generate_images(lines: List[Line], quality=25, global_style=''):
    counter = 1
    for line in tqdm(lines, desc="Generating images"):
        generate_image(line, prefix=f"./tmp/{counter}_", global_style=global_style)
        counter += 1