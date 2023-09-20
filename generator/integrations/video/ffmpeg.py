import ffmpeg
from ...models import SpeechClip
from typing import List
import os
import textwrap
from tqdm import tqdm

def generate_movie(
        dialogs: List[SpeechClip],
        font: str,
        output_path="output.mp4",
        width:int=720,
        height:int=1280,
        clip_buffer_seconds=0.2,  # how much time to wait after characters finish talking
        min_clip_length=1.5,  # minimum time to hold on a clip
        speaking_delay_seconds=0.1, # how long after the clip the audio kicks in
        caption_max_width=30,
    ):

    # If you want to add a shadow:
    shadow_style = ":shadowcolor=black@0.7:shadowx=3:shadowy=3"
    
    # If you want to add a transparent grey background box:
    box_style = ":box=1:boxcolor=black@0.4:boxborderw=10"

    # Choose your style:
    subtitle_style = shadow_style  # Change this to box_style to try the other style

    intermediate_clips = []
    for i, dialog in enumerate(tqdm(dialogs, "Rendering intermediate video clips")):
        image_path = dialog.image
        
        try:
            audio_duration = float(ffmpeg.probe(dialog.audio)['streams'][0]['duration'])
        except Exception as e:
            print(f"Error probing audio duration: {e}")
            continue

        duration = audio_duration + clip_buffer_seconds + speaking_delay_seconds
        duration = max(duration, min_clip_length)

        # Simplify caption logic using textwrap
        wrapped_caption = textwrap.fill(dialog.caption, width=caption_max_width)
        
        try:
            # create each clip of dialog as a separate video
            video_input = ffmpeg.input(image_path, loop=1, framerate=24)
            speaking_delay_ms =speaking_delay_seconds*1000
            audio_input = (
                ffmpeg
                .input(dialog.audio)
                .filter('adelay', f'{speaking_delay_ms}|{speaking_delay_ms}')
                .filter('apad')
            )

            # Modify the video input to include subtitles
            subtitle_y_ratio_from_bottom = 7/24
            video_with_subtitles = video_input.filter(
                'drawtext',
                text=wrapped_caption,
                fontfile=font,
                fontsize=42,
                fontcolor='white',
                text_align="M+C", # had to dig deep into FFmpeg source code to learn that you combine flags with a plus sign
                x='(w - text_w) / 2',
                y=f'(h - (text_h / 2)) - h*{subtitle_y_ratio_from_bottom}', **{
                "shadowcolor": "black@0.7",
                "shadowx": -4,
                "shadowy": 4,
            } if subtitle_style == shadow_style else {
                "box": 1,
                "boxcolor": "black@0.4",
                "boxborderw": 10
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
            continue

    print("Rendering final output...")
    concatenate_videos(intermediate_clips, output_path)

    # Cleanup temporary files
    for clip in intermediate_clips:
        os.remove(clip)


def concatenate_videos(file_list, output_filename):
    # Create input sets for each file in the list
    input_clips = [ffmpeg.input(f) for f in file_list]
    
    # Split the video and audio streams
    video_streams = [clip.video for clip in input_clips]
    audio_streams = [clip.audio for clip in input_clips]
    
    # Concatenate each stream type separately
    concatenated_video = ffmpeg.concat(*video_streams, v=1, a=0)
    concatenated_audio = ffmpeg.concat(*audio_streams, v=0, a=1)
    
    # Output the concatenated streams
    ffmpeg.output(concatenated_video, concatenated_audio, output_filename, acodec='mp3').overwrite_output().run(quiet=True)