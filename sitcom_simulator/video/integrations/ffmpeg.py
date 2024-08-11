import random
from ...models import Script, Clip
from typing import List
import os
import textwrap
from tqdm import tqdm
import tempfile
import atexit
from dataclasses import dataclass
import math
from typing import Literal

FRAME_RATE = 24
MAX_CLIP_SECONDS = 15
FFMPEG_QUALITY:Literal["ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow"] = "slow"

@dataclass
class ShadowSettings:
    """
    Settings for shadows in a video.

    :param color: The color of the shadow
    :param alpha: The alpha of the shadow
    :param x: The x offset of the shadow
    :param y: The y offset of the shadow
    """
    color: str = 'black'
    alpha: float = 0.7
    x: int = 5
    y: int = 5

    def to_dict(self):
        """
        Returns a dictionary representation of the shadow settings for use in an FFmpeg filter.
        """
        return {
            "shadowcolor": f"{self.color}@{self.alpha}",
            "shadowx": self.x,
            "shadowy": self.y
        }

@dataclass
class BoxSettings:
    """
    Settings for boxes in a video.

    :param color: The color of the box
    :param alpha: The alpha of the box
    :param border_width: The width of the box border
    """
    color: str = 'black'
    alpha: float = 0.5
    border_width: int = 10

    def to_dict(self):
        """
        Returns a dictionary representation of the box settings for use in an FFmpeg filter.
        """
        return {
            "box": 1,
            "boxcolor": f"{self.color}@{self.alpha}",
            "boxborderw": self.border_width
        }

@dataclass
class CaptionSettings:
    """
    Settings for captions in a video.

    :param font: The path to the font file to use for the captions
    :param max_width: The maximum width of the captions, in characters
    :param y_ratio_from_bottom: The y ratio from the bottom of the screen to place the captions
    """
    font: str = 'Arial'
    max_width: int = 30
    y_ratio_from_bottom: float = 6/24

    def formatted_caption(self, text: str):
        """
        Renders a caption with the given text and returns the caption string.

        :param text: The text of the caption
        :param width: The width of the video
        :param height: The height of the video
        """
        return textwrap.fill(text, width=self.max_width)
    
@dataclass
class ClipSettings:
    """
    Settings for rendering video clips.
    
    :param clip_buffer_seconds: How much time to wait after characters finish talking
    :param min_clip_seconds: The minimum time to hold on a clip
    :param speaking_delay_seconds: Delay before the audio kicks in
    :param max_zoom_factor: The maximum zoom factor for the pan and zoom effect
    :param min_zoom_factor: The minimum zoom factor for the pan and zoom effect. At least some zoom is necessary for panning.
    :param max_pan_speed: The maximum speed of the pan and zoom effect
    """
    clip_buffer_seconds:float=0.15
    min_clip_seconds:float=1.5
    speaking_delay_seconds:float=0.12
    max_zoom_factor:float=1.3 # magic number that seems to work well
    min_zoom_factor:float=1.05 # magic number that seems to work well
    max_pan_speed:float=6 # magic number that seems to work well

failed_image_captions = [
    "This image has been seized by the FBI",
    "REDACTED",
    "This image has been classified",
    "CENSORED",
    "This image has been confiscated",
    "This image has been banned in your country",
    "This image has been quarantined",
    "[image too dangerous to be seen by human eyes]",
    "[Intense Violence]",
    "[Innappropriate Content]",
    "[Explicit Content]",
    "[Scandalous Content]",
    "Image seized by the government",
]

def render_clip(
        clip: Clip,
        width:int=720,
        height:int=1280,
        speed:float=1.0,
        pan_and_zoom:bool=True,
        clip_settings:ClipSettings=ClipSettings(),
        caption_settings:CaptionSettings=CaptionSettings(),
        caption_bg_settings:BoxSettings|ShadowSettings=BoxSettings(),
        audio_codec:Literal['mp3', 'aac']='mp3',
    ):
    """
    Renders a video clip from the given clip object and returns the path to the rendered video file.

    :param clip: The clip to render
    :param width: The width of the video
    :param height: The height of the video
    :param speed: The speed of the final video. 1.0 is normal speed
    :param pan_and_zoom: If True, the pan and zoom effect on images will be enabled
    :param clip_settings: The settings for rendering the video clip
    :param caption_settings: The settings for the captions
    :param caption_bg_settings: The settings for the caption background
    :param audio_codec: The audio codec to use for the output video
    """
    width = int(round(width))
    height = int(round(height))

    import ffmpeg
    caption = clip.speech or clip.title
    title_clip = not not clip.title
    if caption:
        caption = caption_settings.formatted_caption(caption)

    scale_factor = min(width, height) / 720 # 720 is the reference screen width
    
    if clip.audio_path:
        try:
            audio_path = clip.audio_path.replace('/', '\\') if os.name == 'nt' else clip.audio_path
            audio_duration = float(ffmpeg.probe(audio_path)['streams'][0]['duration']) if clip.audio_path else 0
        except Exception as e:
            print(f"Error probing audio duration: {e}.\nHave you put ffmpeg and ffprobe binaries into the root project directory?")
            print(clip.audio_path)
            audio_duration = 0
    else:
        audio_duration = 0

    duration = audio_duration + clip_settings.clip_buffer_seconds + clip_settings.speaking_delay_seconds
    duration = max(duration, clip_settings.min_clip_seconds)
    duration = min(duration, MAX_CLIP_SECONDS) # maximum duration for a clip (to prevent long AI audio glitches)
    duration = duration / speed
    if clip.duration and not clip.speaker: # 'not speaker' in case the llm forgets proper syntax
        duration = clip.duration
    
    no_image = clip.image_path is None
    seized_image = clip.image_path is None and not title_clip

    if no_image or seized_image:
        video_input = ffmpeg.input(f'color=c=black:s={width}x{height}:d=5', f='lavfi')
    else:
        video_input = ffmpeg.input(clip.image_path, loop=1, framerate=FRAME_RATE)
        # the zoom effect is jittery for some strange reason
        # but if we upscale the image first, the jitter is less noticeable
        # at the cost of slower rendering
        prezoom_scale_factor = 2 if pan_and_zoom else 1
        prezoom_scale_width = int(width * prezoom_scale_factor)
        prezoom_scale_height = int(height * prezoom_scale_factor)
        video_input = (
            video_input
            .filter('scale', prezoom_scale_width, prezoom_scale_height, force_original_aspect_ratio="increase")
            .filter('crop', prezoom_scale_width, prezoom_scale_height)
        )
        if pan_and_zoom:
            zoom_start = clip_settings.min_zoom_factor  # Start with no zoom
            zoom_end = random.uniform(clip_settings.min_zoom_factor, clip_settings.max_zoom_factor)  # Target end zoom level, adjust as needed
            zoom_out = random.choice([True, False])  # Randomly zoom in or out
            if zoom_out:
                zoom_start, zoom_end = zoom_end, zoom_start  # Reverse the zoom levels for a zoom out effect
            total_frames = int(duration * FRAME_RATE)  # Total frames based on video duration and frame rate

            # Ensure zoom continues smoothly for the entire duration
            zoom_expr = f'{zoom_start}+(on/{total_frames})*{zoom_end-zoom_start}'

            # Randomly pan the image 
            max_pan = clip_settings.max_pan_speed * (min(width, height) / 720) * prezoom_scale_factor  # Maximum pan speed (pixels per frame, scaled to 720p reference screen width
            # the sqrt(total_frames) is to make the pan speed scale with the duration of the clip
            # so that shorter clips are punchier and longer clips are smoother
            frame_offset = f"((on-{total_frames/2})/{math.sqrt(total_frames)})"
            x_expr = f'(iw/2.0-(iw/zoom/2.0))+{random.uniform(-max_pan, max_pan)}*{frame_offset}'
            y_expr = f'(ih/2.0-(ih/zoom/2.0))+{random.uniform(-max_pan, max_pan)}*{frame_offset}'

            video_input = video_input.zoompan(
                z=zoom_expr, 
                x=x_expr, 
                y=y_expr, 
                d=1,  # Apply the effect continuously across frames
                s=f'{width}x{height}', 
                fps=FRAME_RATE,
                )

    speaking_delay_ms = clip_settings.speaking_delay_seconds * 1000

    # make sure every clip has an audio track, even if it's silent
    if clip.audio_path is None:
        audio_input = ffmpeg.input('anullsrc', format='lavfi', t=duration).audio
    else:
        audio_input = (
            ffmpeg
            .input(clip.audio_path)
            .filter('adelay', f'{speaking_delay_ms}|{speaking_delay_ms}')
            .filter('apad', pad_dur=duration)
            .filter('atempo', speed)
            .filter('speechnorm')
        )

    caption_bg_dict = caption_bg_settings.to_dict() if isinstance(caption_bg_settings, BoxSettings) else caption_bg_settings.to_dict()
    
    if caption or seized_image:
        video_input = video_input.filter(
            'drawtext',
            text=caption if caption else random.choice(failed_image_captions),
            fontfile=caption_settings.font,
            fontsize=48 * scale_factor, # scales the font size with 720px as the reference screen width
            fontcolor='white',
            text_align="M+C", # had to dig deep into FFmpeg source code to learn that you combine flags with a plus sign
            x='(w - text_w) / 2',
            y=f'(h - (text_h / 2)) - h*{caption_settings.y_ratio_from_bottom if not title_clip else 0.5}',
            **caption_bg_dict,
        )

    video_input = video_input.filter('setpts', f'PTS/{speed}')

    try:
        input_streams = [video_input] if audio_input is None else [video_input, audio_input]
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            intermediate_clip = (
                ffmpeg.output(*input_streams, temp_file.name, vcodec='libx264', preset='superfast', acodec=audio_codec, t=duration)
                .overwrite_output()
                .run(capture_stderr=True, overwrite_output=True)
            )
            atexit.register(os.remove, temp_file.name)
            return temp_file.name
    except ffmpeg.Error as e:
        print('FFmpeg Error:', e.stderr.decode() if e.stderr else str(e))  # Decoding the stderr for better readability
        raise Exception(f"ffmpeg error: {e.stderr.decode() if e.stderr else str(e)}")


def concatenate_clips(
        filenames: List[str],
        output_filename: str,
        background_music:str|None=None,
        bgm_volume:float=-24,
        audio_codec:Literal['mp3', 'aac']='mp3',
        ):
    """
    Combines the given video clips into a single video file and returns the path to the concatenated video file.

    :param filenames: The list of video file paths to combine
    :param output_filename: The name of the output file
    :param background_music: The path to the background music file
    :param bgm_volume: The volume of the background music, between 0 and 1
    :param audio_codec: The audio codec to use for the output video
    """
    import ffmpeg

    # Create input sets for each file in the list
    input_clips = [ffmpeg.input(f) for f in filenames]
    
    # Split the video and audio streams
    video_streams = [clip.video for clip in input_clips]
    audio_streams = [clip.audio for clip in input_clips]
    
    # Concatenate each stream type separately
    concatenated_video = ffmpeg.concat(*video_streams, v=1, a=0)
    concatenated_audio = ffmpeg.concat(*audio_streams, v=0, a=1)

    total_audio_duration = sum([float(ffmpeg.probe(f)['streams'][0]['duration']) for f in filenames])
    
    # If background music is provided, adjust its volume and mix it with concatenated audio
    if background_music:
        bgm_input = (
            ffmpeg
            .input(background_music)
            # .filter('volume', str(bgm_volume)) # old way, ~.25 worked well
            .filter('loudnorm', i=bgm_volume) # new way, more consistent
            .filter('atrim', duration=total_audio_duration)
        )
        concatenated_audio = ffmpeg.filter([concatenated_audio, bgm_input], 'amix')  # Mix concatenated audio and bgm

    sanitized_filename = output_filename.replace(':', '').replace('?', '')

    # Output the concatenated streams
    (
        ffmpeg
        .output(
            concatenated_video,
            concatenated_audio,
            sanitized_filename,
            vcodec='libx264',
            pix_fmt='yuv420p', # necessary for compatibility
            acodec=audio_codec,
            r=FRAME_RATE,
            preset=FFMPEG_QUALITY,
            **{'b:v': '8000K'}
            )
        .overwrite_output()
        .run(capture_stderr=True)
    )

    return sanitized_filename

def render_video(
        script: Script,
        output_path: str='output.mp4',
        width:int=720,
        height:int=1280,
        speed:float=1.0,
        pan_and_zoom:bool=True,
        clip_settings:ClipSettings=ClipSettings(),
        caption_settings:CaptionSettings=CaptionSettings(),
        caption_bg_settings:BoxSettings|ShadowSettings=BoxSettings(),
        bgm_volume:float=-24,
        audio_codec:Literal['mp3', 'aac']='mp3',
    ):
    """
    Renders a video from the given script and returns the path to the rendered video file.

    At present, only 9:16 aspect ratio is supported, but 16:9 and 1:1 will be supported in the future.

    :param script: The script to render
    :param output_path: The path to save the rendered video
    :param width: The width of the video
    :param height: The height of the video
    :param speed: The speed of the final video. 1.0 is normal speed
    :param pan_and_zoom: If True, the pan and zoom effect on images will be enabled
    :param clip_settings: The settings for rendering the video clip
    :param caption_settings: The settings for the captions
    :param caption_bg_settings: The settings for the caption background
    :param bgm_volume: The volume of the background music, good values are between -24 and -16
    :param audio_codec: The audio codec to use for the output video
    """
    intermediate_clips = []    
    for clip in tqdm(script.clips, desc="Rendering intermediate video clips"):
        clip_file = render_clip(
            clip=clip,
            width=width,
            height=height,
            clip_settings=clip_settings,
            caption_settings=caption_settings,
            caption_bg_settings=caption_bg_settings,
            speed=speed,
            pan_and_zoom=pan_and_zoom,
            audio_codec=audio_codec,
        )
        intermediate_clips.append(clip_file)

    print("Rendering final video...")
    final_video_path = concatenate_clips(
        intermediate_clips,
        output_path,
        background_music=script.metadata.bgm_path,
        bgm_volume=bgm_volume,
        audio_codec=audio_codec,
    )
    
    return final_video_path