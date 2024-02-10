from .integrations import fakeyou as fakeyou
from .integrations import gtts as gtts
from typing import List, Literal
from sitcom_simulator.models import Script
from typing import Optional, Callable

Engine = Literal["fakeyou", "gtts"]

def generate_voices(
        script: Script,
        engine:Engine="fakeyou",
        on_voice_generated: Optional[Callable[[int, str], None]] = None
        ):
    """
    Generates and returns a list of voice clip paths for the given script using the given engine.
    
    More procedural in nature than add_voices.
    This function is typically not used directly, since add_voices is more pleasant to work with.
    
    :param script: The script to generate voice clips for
    :param engine: The engine to use for generating voice clips
    :param on_voice_generated: A callback to call after each voice clip is generated which takes the clip index and path to the generated audio
    """
    # generating voice clips can take a LONG time if args.high_quality_audio == True
    # because of long delays to avoid API timeouts on FakeYou.com
    if engine == "fakeyou":
        audio_urls = fakeyou.generate_voices(script, on_voice_generated)
        audio_paths = [fakeyou.download_voice(audio_url) if audio_url else None for audio_url in audio_urls]
    else:
        audio_paths = gtts.generate_voices(script, on_voice_generated)
    return audio_paths


def add_voices(
        script: Script,
        engine:Engine="fakeyou",
        on_voice_generated: Optional[Callable[[int, str], None]] = None
        ):
    """
    Given a script, returns the same script but with the audio paths filled in.
    
    More functional in nature than generate_voices.

    :param script: The script to add voices to
    :param engine: The engine to use for generating voice clips
    :param on_voice_generated: A callback to call after each voice clip is generated which takes the clip index and path to the generated audio
    """
    audio_paths = generate_voices(script, engine=engine, on_voice_generated=on_voice_generated)
    return script.replace(clips=[clip.replace(audio_path=audio_path) for clip, audio_path in zip(script.clips, audio_paths)])