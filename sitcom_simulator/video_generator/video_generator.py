from typing import List
from ..models import Script
from .integrations import ffmpeg

def render_video(
        script: Script,
        font: str,
        output_path="output.mp4",
        width:int=1080,
        height:int=1920,
        clip_buffer_seconds=0.35, # how much time to wait after characters finish talking
        min_clip_length=1.5, # minimum time to hold on a clip
    ):
    return ffmpeg.render_video(
        script=script,
        font=font,
        output_path=output_path,
        width=width,
        height=height,
        clip_buffer_seconds=clip_buffer_seconds,
        min_clip_length=min_clip_length
    )