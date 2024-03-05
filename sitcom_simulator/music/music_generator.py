from typing import Literal, Callable, Optional
import random
from sitcom_simulator.models import Script
import logging

Engine = Literal["freepd"]

def generate_music(
        category: str | None,
        engine:Engine="freepd",
        music_url: str | None = None,
        ) -> tuple[str, str]:
    """
    Generates and returns a path to a music file using the given engine.

    More procedural in nature than add_music.

    :param category: The category of music to generate
    :param engine: The engine to use for generating music
    :param music_url: The URL of the music to use. If provided, category is ignored.

    :return: The path to the generated music file and the url of the music to use
    """
    from .integrations import freepd
    if engine == "freepd":
        if music_url:
            logging.debug(f"Using music from URL: {music_url}")
            return freepd.download_file(music_url), music_url
        logging.debug(f"Generating music: {category}")
        try:
            freepd_category = freepd.MusicCategory(category)
        except ValueError:
            freepd_category = None
        if freepd_category is None:
            freepd_category = random.choice(list(freepd.MusicCategory))
        return freepd.download_random_music(freepd_category)
    else:
        raise ValueError(f"Invalid engine: {engine}")

def add_music(
        script: Script,
        engine:Engine="freepd",
        music_url: str | None = None,
        on_music_generated: Optional[Callable[[str], None]] = None,
        ):
    """
    Given a script, returns the same script but with the music path filled in.

    More functional in nature than generate_music.

    :param script: The script to add music to
    :param engine: The engine to use for generating music
    :param music_url: The URL of the music to use. If provided, category is ignored.
    :param on_music_generated: A callback to call after the music is generated which takes the path to the generated music
    """
    music_path, music_url = generate_music(category=script.metadata.bgm_style, music_url=music_url, engine=engine)
    if on_music_generated:
        on_music_generated(music_path)
    return script.replace(metadata=script.metadata.replace(bgm_path=music_path, bgm_url=music_url))