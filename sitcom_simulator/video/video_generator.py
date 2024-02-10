from typing import List
from ..models import Script
from .integrations import ffmpeg

def render_video(
        script: Script,
        font: str,
        output_path="output.mp4",
        width:int=1080,
        height:int=1920,
        clip_buffer_seconds=0.35,
        min_clip_length=1.5,
    ):
    """
    Renders a video from the given script and returns the path to the rendered video.

    :param script: The script to render
    :param font: The path to the font file to use
    :param output_path: The path to save the rendered video to
    :param width: The width of the video to render
    :param height: The height of the video to render
    :param clip_buffer_seconds: How much time to wait after characters finish talking
    :param min_clip_length: The minimum time to hold on a clip
    """
    return ffmpeg.render_video(
        script=script,
        font=font,
        output_path=output_path,
        width=width,
        height=height,
        clip_buffer_seconds=clip_buffer_seconds,
        min_clip_length=min_clip_length
    )