import ffmpeg
from ...models import SpeechClip
from typing import List
import os
import textwrap
from tqdm import tqdm

def generate_movie(
        dialogs: List[SpeechClip],
        background_music: str | None,
        font: str,
        output_path="output.mp4",
        width:int=720,
        height:int=1280,
        clip_buffer_seconds=0.15,  # how much time to wait after characters finish talking
        min_clip_length=1.5,  # minimum time to hold on a clip
        speaking_delay_seconds=0.12, # how long after the clip the audio kicks in
        caption_max_width=30,
    ):

    # If you want to add a shadow:
    shadow_style = ":shadowcolor=black@0.7:shadowx=3:shadowy=3"
    
    # If you want to add a transparent grey background box:
    box_style = ":box=1:boxcolor=black@0.4:boxborderw=10"

    subtitle_style = box_style # + box_style  # mix and match as desired

    intermediate_clips = []
    for i, dialog in enumerate(tqdm(dialogs, "Rendering intermediate video clips")):
        image_path = dialog.image
        
        try:
            audio_duration = float(ffmpeg.probe(dialog.audio.replace('/', '\\'))['streams'][0]['duration'])
        except Exception as e:
            print(f"Error probing audio duration: {e}.\nHave you put ffmpeg and ffprobe binaries into the root project directory?")
            raise e

        duration = audio_duration + clip_buffer_seconds + speaking_delay_seconds
        duration = max(duration, min_clip_length)

        # Simplify caption logic using textwrap
        wrapped_caption = textwrap.fill(dialog.caption, width=caption_max_width)
        
        try:
            # create each clip of dialog as a separate video
            video_input = (
                ffmpeg.input(image_path, loop=1, framerate=24)
                .filter('scale', width, '-1')
            )
            speaking_delay_ms =speaking_delay_seconds*1000
            audio_input = (
                ffmpeg
                .input(dialog.audio)
                .filter('adelay', f'{speaking_delay_ms}|{speaking_delay_ms}')
                .filter('apad')
            )

            # Modify the video input to include subtitles
            subtitle_y_ratio_from_bottom = 6/24
            scale_factor = width / 720
            video_with_subtitles = video_input.filter(
                'drawtext',
                text=wrapped_caption,
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

            temp_clip_path = f'tmp/temp_{i}.mp4'
            clip = (
                ffmpeg
                .output(video_with_subtitles, audio_input, temp_clip_path, t=duration, vcodec='libx264', acodec='mp3')
                .run(quiet=True)
            )
            intermediate_clips.append(temp_clip_path)

        except Exception as e:
            print(f"Error processing dialog: {e}")
            raise e

    print("Rendering final output to", output_path, "...")
    concatenate_videos(intermediate_clips, output_path, background_music)

    # Cleanup temporary files
    for clip in intermediate_clips:
        os.remove(clip)


def concatenate_videos(file_list, output_filename, background_music=None, bgm_volume=0.25):

    # Create input sets for each file in the list
    input_clips = [ffmpeg.input(f) for f in file_list]
    
    # Split the video and audio streams
    video_streams = [clip.video for clip in input_clips]
    audio_streams = [clip.audio for clip in input_clips]
    
    # Concatenate each stream type separately
    concatenated_video = ffmpeg.concat(*video_streams, v=1, a=0)
    concatenated_audio = ffmpeg.concat(*audio_streams, v=0, a=1)

    total_audio_duration = sum([float(ffmpeg.probe(f)['streams'][0]['duration']) for f in file_list])
    
    # If background music is provided, adjust its volume and mix it with concatenated audio
    if background_music:
        bgm_input = (
            ffmpeg
            .input(background_music)
            .filter('volume', str(bgm_volume))
            .filter('atrim', duration=total_audio_duration)
        )
        concatenated_audio = ffmpeg.filter([concatenated_audio, bgm_input], 'amix')  # Mix concatenated audio and bgm

    # Output the concatenated streams
    (
        ffmpeg
        .output(
            concatenated_video,
            concatenated_audio,
            output_filename.replace(':', '').replace('?',''),
            vcodec='libx264',
            pix_fmt='yuv420p', # necessary for compatibility
            acodec='mp3',
            r=24,
            **{'b:v': '8000K'}
            )
        .overwrite_output()
        .run()
    )