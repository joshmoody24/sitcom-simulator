from tqdm import tqdm
from typing import List, Optional, Callable, Literal
from sitcom_simulator.models import Script
import os
import atexit

Engine = Literal["stability", "pillow"]

def generate_images(
        script: Script,
        width=768,
        height=1344,
        on_image_generated: Optional[Callable[[int, str], None]] = None,
        engine:Engine="stability",
    ):
    """
    Generates and returns a list of image paths for the given script.

    More procedural in nature than add_images.
    
    :param script: The script to generate images for
    :param width: The width of the images to generate
    :param height: The height of the images to generate
    :param on_image_generated: A callback to call after each image is generated which takes the clip index and path to the generated image
    :param engine: The engine to use for generating images
    """
    from .integrations import stability, pillow
    image_paths: List[str | None] = []
    for i, clip in tqdm(enumerate(script.clips), desc="Generating images", total=len(script.clips)):
        image_prompt = clip.image_prompt
        if not image_prompt:
            image_paths.append(None)
            continue
        if clip.image_path:
            image_paths.append(clip.image_path)
            continue
        if engine == "stability":
            full_prompt = f'{image_prompt}{", " + script.metadata.art_style if script.metadata.art_style else ""}' 
            image_path = stability.generate_image(prompt=full_prompt, width=width, height=height)
        else: # debug engine
            image_path = pillow.generate_image(width, height)
        atexit.register(os.remove, image_path)
        image_paths.append(image_path)
        if on_image_generated:
            on_image_generated(i, image_path)

    return image_paths

def add_images(
        script: Script,
        width=768,
        height=1344,
        on_image_generated: Optional[Callable[[int, str], None]] = None,
        engine:Engine="stability",
    ) -> Script:
    """
    Given a script, returns the same script but with the image paths filled in.

    More functional in nature than generate_images.

    :param script: The script to add images to
    :param width: The width of the images to generate
    :param height: The height of the images to generate
    :param on_image_generated: A callback to call after each image is generated which takes the clip index and path to the generated image
    :param engine: The engine to use for generating images
    """
    image_paths = generate_images(
        script=script,
        width=width,
        height=height,
        on_image_generated=on_image_generated,
        engine=engine)
    return script.replace(clips=[clip.replace(image_path=image_path) for clip, image_path in zip(script.clips, image_paths)])