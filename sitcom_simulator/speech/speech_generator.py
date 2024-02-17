from typing import List, Literal
from sitcom_simulator.models import Script
from typing import Optional, Callable

Engine = Literal["fakeyou", "gtts"]

def generate_voices(
        script: Script,
        engine:Engine="fakeyou",
        on_voice_downloaded: Optional[Callable[[int, str], None]] = None,
        fakeyou_on_voice_url_generated: Optional[Callable[[int, str], None]] = None,
        fakeyou_job_delay:int=30,
        fakeyou_poll_delay:int=10,
        ):
    """
    Generates and returns a list of voice clip paths for the given script using the given engine.
    
    More procedural in nature than add_voices.
    This function is typically not used directly, since add_voices is more pleasant to work with.
    
    :param script: The script to generate voice clips for
    :param engine: The engine to use for generating voice clips
    :param on_voice_downloaded: A callback to call after each voice clip is downloaded which takes the clip index and path to the downloaded audio
    :param fakeyou_on_voice_url_generated: A callback to call after each FakeYou voice clip is generated which takes the clip index and url of the generated audio
    :param fakeyou_job_delay: The number of seconds to wait between starting audio generation jobs. Lower values render faster but are more likely to get rate limited
    :param fakeyou_poll_delay: The number of seconds to wait between polling for audio generation job completion
    """
    from .integrations import fakeyou as fakeyou
    from .integrations import gtts as gtts
    # generating voice clips can take a LONG time if args.high_quality_audio == True
    # because of long delays to avoid API timeouts on FakeYou.com
    if engine == "fakeyou":
        audio_urls = fakeyou.generate_voices(
            script,
            fakeyou_on_voice_url_generated,
            fakeyou_job_delay,
            fakeyou_poll_delay,
        )
        audio_paths = []
        for i, audio_url in enumerate(audio_urls):
            if audio_url is None: continue
            audio_path = fakeyou.download_voice(audio_url)
            audio_paths.append(audio_path)
            if on_voice_downloaded:
                on_voice_downloaded(i, audio_path)
        return audio_paths
    else:
        audio_paths = gtts.generate_voices(script, on_voice_downloaded)
    return audio_paths


def add_voices(
        script: Script,
        engine:Engine="fakeyou",
        on_voice_generated: Optional[Callable[[int, str], None]] = None,
        audio_job_delay:int=30,
        audio_poll_delay:int=10,
        ):
    """
    Given a script, returns the same script but with the audio paths filled in.
    
    More functional in nature than generate_voices.

    :param script: The script to add voices to
    :param engine: The engine to use for generating voice clips
    :param on_voice_generated: A callback to call after each voice clip is generated which takes the clip index and path to the generated audio
    :param audio_job_delay: The number of seconds to wait between starting audio generation jobs. Lower values render faster but are more likely to get rate limited. (FakeYou only)
    :param audio_poll_delay: The number of seconds to wait between polling for audio generation job completion. (FakeYou only)
    """
    audio_paths = generate_voices(
        script,
        engine=engine,
        fakeyou_on_voice_url_generated=on_voice_generated,
        fakeyou_job_delay=audio_job_delay,
        fakeyou_poll_delay=audio_poll_delay,
    )
    return script.replace(clips=[clip.replace(audio_path=audio_path) for clip, audio_path in zip(script.clips, audio_paths)])