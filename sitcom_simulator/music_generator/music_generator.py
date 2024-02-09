from .integrations import freepd
from typing import Literal, Callable, Optional
import random
from sitcom_simulator.models import Script
import logging

Engine = Literal["freepd"]

def generate_music(
        category: str | None,
        engine:Engine="freepd",
        ):
    if engine == "freepd":
        logging.debug(f"Generating music: {category}")
        try:
            freepd_category = freepd.MusicCategory(category)
        except ValueError:
            freepd_category = None
        if freepd_category is None:
            freepd_category = random.choice(list(MusicCategory))
        return freepd.download_random_music(freepd_category)
    else:
        raise ValueError(f"Invalid engine: {engine}")

def add_music(
        script: Script,
        engine:Engine="freepd",
        category: str | None = None,
        on_music_generated: Optional[Callable[[str], None]] = None
        ):
    music_path = generate_music(category)
    if on_music_generated:
        on_music_generated(music_path)
    return script.replace(metadata=script.metadata.replace(bgm_path=music_path))

MusicCategory = freepd.MusicCategory