from .models import SpeechClip
from typing import List
from .integrations.video import ffmpeg, moviepy

# example input
'''
[{
    caption='Itsa me, Mario',
    image=./path/to/image,
    audio=./path/to/audio
}]
'''

VIDEO_HEIGHT = 1280
VIDEO_WIDTH = 720

def generate_movie(
        dialogs: List[SpeechClip],
        font: str,
        output_path="output.mp4",
        width:int=720,
        height:int=1280,
        clip_buffer_seconds=0.35, # how much time to wait after characters finish talking
        min_clip_length=1.5, # minimum time to hold on a clip
    ):
    return ffmpeg.generate_movie(
        dialogs,
        font,
        output_path,
        width,
        height,
        clip_buffer_seconds,
        min_clip_length
    )