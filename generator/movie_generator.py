from .models import SpeechClip
from typing import List
from .integrations.video import ffmpeg, moviepy

def generate_movie(
        dialogs: List[SpeechClip],
        background_music: str | None,
        font: str,
        output_path="output.mp4",
        width:int=1080,
        height:int=1920,
        clip_buffer_seconds=0.35, # how much time to wait after characters finish talking
        min_clip_length=1.5, # minimum time to hold on a clip
    ):
    return ffmpeg.generate_movie(
        dialogs,
        background_music,
        font,
        output_path,
        width,
        height,
        clip_buffer_seconds,
        min_clip_length
    )