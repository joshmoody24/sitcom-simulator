import ffmpeg
from ...models import SpeechClip
from typing import List
import tempfile
import os

def generate_movie(
        dialogs: List[SpeechClip],
        font: str,
        output_path="output.mp4",
        width:int=720,
        height:int=1280,
        clip_buffer_seconds=0.35, # how much time to wait after characters finish talking
        min_clip_length=1.5, # minimum time to hold on a clip
    ):
    intermediate_clips = []

    for dialog in dialogs:
        image_path = dialog.image
        
        audio_duration = float(ffmpeg.probe(dialog.audio)['streams'][0]['duration'])
        duration = audio_duration + clip_buffer_seconds
        if duration < min_clip_length:
            duration = min_clip_length

        # Generate caption using the same logic you had
        raw_caption = dialog.caption
        raw_caption_queue = raw_caption
        caption = ""
        max_chars_per_line = 30
        char_counter = 0
        while len(raw_caption_queue) > 0:
            split = raw_caption_queue.split(' ')
            if char_counter + len(split[0]) + 1 < max_chars_per_line:
                caption += " "
                char_counter += 1
            else:
                caption += "\n"
                char_counter = 0
            caption += split[0]
            char_counter += len(split[0])
            raw_caption_queue = " ".join(split[1:])
        
        # Temporary path to store the intermediate clip
        temp_clip_path = tempfile.mktemp(suffix=".mp4")

        # Combine audio, image and text using ffmpeg-python
        input_stream = ffmpeg.input(image_path, t=duration)
        audio_stream = ffmpeg.input(dialog.audio).audio

        video_stream = (
            input_stream.output('pipe:', vf='fps=24,scale={}:{}'.format(width, height), format='rawvideo', pix_fmt='rgb24')
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # Create the text clip using ffmpeg drawtext filter
        video_with_text = (
            ffmpeg.input('pipe:', format='rawvideo', pix_fmt='rgb24', s='{}x{}'.format(width, height), r=24)
            .filter('drawtext', text=caption, fontsize=48, fontcolor='white', x='(w-tw)/2', y=height-48, fontfile=font)
            .output(temp_clip_path, vf='fps=24', pix_fmt='yuv420p', vcodec='libx264')
            .audio
            .filter('adelay', "{}|{}".format(int(clip_buffer_seconds * 1000), int(clip_buffer_seconds * 1000)))
            .audio
            .input(dialog.audio)
            .audio
            .concat(n=2, v=0, a=1)
            .audio
            .run(capture_stdout=True, capture_stderr=True)
        )

        intermediate_clips.append(temp_clip_path)

    # Concatenate all clips
    ffmpeg.concat(*[ffmpeg.input(clip) for clip in intermediate_clips]).output(output_path).run()

    # Cleanup temporary files
    for clip in intermediate_clips:
        os.remove(clip)