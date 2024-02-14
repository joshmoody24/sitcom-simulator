from ...models import Script, Clip
from typing import List
import os
import textwrap
from tqdm import tqdm
import tempfile
import atexit

def render_clip(
        clip: Clip,
        font: str,
        width:int=720,
        height:int=1280,
        clip_buffer_seconds:float=0.15,
        min_clip_seconds:float=1.5,
        speaking_delay_seconds:float=0.12,
        caption_max_width:int=30,
    ):
    """
    Renders a video clip from the given clip object and returns the path to the rendered video file.

    :param clip: The clip to render
    :param font: The path to the font file to use for the captions
    :param width: The width of the video
    :param height: The height of the video
    :param clip_buffer_seconds: How much time to wait after characters finish talking
    :param min_clip_seconds: The minimum time to hold on a clip
    :param speaking_delay_seconds: Delay before the audio kicks in
    :param caption_max_width: The maximum width of the captions, in characters
    """
    import ffmpeg
    caption = clip.speech
    if caption:
        caption = textwrap.fill(caption, width=caption_max_width)

    subtitle_y_ratio_from_bottom = 6/24
    scale_factor = width / 720

    # If you want to add a shadow:
    shadow_style = ":shadowcolor=black@0.7:shadowx=3:shadowy=3"
    # If you want to add a transparent grey background box:
    box_style = ":box=1:boxcolor=black@0.4:boxborderw=10"
    subtitle_style = box_style # + box_style  # mix and match as desired
    
    try:
        audio_path = clip.audio_path.replace('/', '\\') if os.name == 'nt' else clip.audio_path
        audio_duration = float(ffmpeg.probe(audio_path)['streams'][0]['duration']) if clip.audio_path else 0
    except Exception as e:
        print(f"Error probing audio duration: {e}.\nHave you put ffmpeg and ffprobe binaries into the root project directory?")
        print(clip.audio_path)
        audio_duration = 0

    duration = audio_duration + clip_buffer_seconds + speaking_delay_seconds
    duration = max(duration, min_clip_seconds)
    if clip.duration and not clip.speaker: # 'not speaker' in case the llm forgets proper syntax
        duration = clip.duration
    
    if clip.image_path is None:
        video_input = ffmpeg.input(f'color=c=black:s={width}x{height}:d=5', f='lavfi')
    else:
        video_input = (
            ffmpeg.input(clip.image_path, loop=1, framerate=24)
            .filter('scale', width, height, force_original_aspect_ratio="increase")
            .filter('crop', width, height)
        )

    speaking_delay_ms =speaking_delay_seconds * 1000

    # make sure every clip has an audio track, even if it's silent
    if clip.audio_path is None:
        audio_input = ffmpeg.input('anullsrc', format='lavfi', t=duration).audio
    else:
        audio_input = (
            ffmpeg
            .input(clip.audio_path)
            .filter('adelay', f'{speaking_delay_ms}|{speaking_delay_ms}')
            .filter('apad', pad_dur=duration)
        )

    # Modify the video input to include subtitles

    if caption:
        video_input = video_input.filter(
            'drawtext',
            text=caption,
            fontfile=font,
            fontsize=42 * scale_factor, # scales the font size with 720px as the reference screen width
            fontcolor='white',
            text_align="M+C", # had to dig deep into FFmpeg source code to learn that you combine flags with a plus sign
            x='(w - text_w) / 2',
            y=f'(h - (text_h / 2)) - h*{subtitle_y_ratio_from_bottom}', **{
            "shadowcolor": "black@0.6",
            "shadowx": -4 * scale_factor,
            "shadowy": 4 * scale_factor,
        } if subtitle_style == shadow_style else {
            "box": 1,
            "boxcolor": "black@0.5",
            "boxborderw": 10 * scale_factor
        })

    try:
        input_streams = [video_input] if audio_input is None else [video_input, audio_input]
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            intermediate_clip = (
                ffmpeg.output(*input_streams, temp_file.name, vcodec='libx264', preset='superfast', acodec='mp3', t=duration)
                .overwrite_output()
                .run()
            )
            atexit.register(os.remove, temp_file.name)
            return temp_file.name
    except ffmpeg.Error as e:
        print('FFmpeg Error:', e.stderr.decode() if e.stderr else str(e))  # Decoding the stderr for better readability
        raise Exception("ffmpeg error:", e.stderr if e.stderr else str(e))


def concatenate_clips(
        filenames: List[str],
        output_filename: str,
        background_music:str|None=None,
        bgm_volume:float=0.25,
        ):
    """
    Combines the given video clips into a single video file and returns the path to the concatenated video file.

    :param filenames: The list of video file paths to combine
    :param output_filename: The name of the output file
    :param background_music: The path to the background music file
    :param bgm_volume: The volume of the background music, between 0 and 1
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
            .filter('volume', str(bgm_volume))
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
            acodec='mp3',
            r=24,
            **{'b:v': '8000K'}
            )
        .overwrite_output()
        .run()
    )

    return sanitized_filename

# TODO: support aspect ratios 16:9 and 1:1
def render_video(
        script: Script,
        font: str,
        output_path: str = 'output.mp4',
        width:int=720,
        height:int=1280,
        clip_buffer_seconds=0.15,
        min_clip_length=1.5,
        speaking_delay_seconds=0.12,
        caption_max_width=30,
    ):
    """
    Renders a video from the given script and returns the path to the rendered video file.

    At present, only 9:16 aspect ratio is supported, but 16:9 and 1:1 will be supported in the future.

    :param script: The script to render
    :param font: The path to the font file to use for the captions
    :param output_path: The path to save the rendered video
    :param width: The width of the video
    :param height: The height of the video
    :param clip_buffer_seconds: How much time to wait after characters finish talking
    :param min_clip_length: The minimum time to hold on a clip
    :param speaking_delay_seconds: Delay before the audio kicks in
    :param caption_max_width: The maximum width of the captions, in characters
    """
    intermediate_clips = []    
    for clip in tqdm(script.clips, desc="Rendering intermediate video clips"):
        clip_file = render_clip(
            clip=clip,
            font=font,
            width=width,
            height=height,
            clip_buffer_seconds=clip_buffer_seconds,
            min_clip_seconds=min_clip_length,
            speaking_delay_seconds=speaking_delay_seconds,
            caption_max_width=caption_max_width,
        )
        intermediate_clips.append(clip_file)
        
    final_video_path = concatenate_clips(intermediate_clips, output_path, background_music=script.metadata.bgm_path)
    
    return final_video_path