from moviepy.editor import *
from ...models import SpeechClip
from typing import List

def generate_movie(dialogueData:List[SpeechClip], font:str, output_path="output.mp4", width:int=720, height:int=1280):
    """
        MoviePy backend for generating videos.
        
        While it still works, it is more limited in functionality than the FFmpeg backend and has thus been deprecated.
    """
    dialogue_clips = []
    for dialogue in dialogueData:

        voiceover = AudioFileClip(dialogue['audio'])

        # calculate the duration
        hang_time = 0.35
        duration = voiceover.duration + hang_time
        min_length = 1.5
        if(duration < min_length):
            duration = min_length

        # black background
        bg = ColorClip(size=(width,height), color=[0,0,0])
        bg = bg.set_duration(duration)
        bg = bg.set_audio(voiceover)

        # the image
        img_clip = ImageClip(dialogue['image'])
        img_clip = img_clip.resize(width/img_clip.w,height/img_clip.h)
        img_clip = img_clip.set_duration(duration)
        img_clip = img_clip.set_fps(24)
        img_clip = img_clip.set_position(('center', 'top'))

        # the caption
        raw_caption = dialogue["caption"]
        raw_caption_queue = raw_caption
        caption = ""
        # generate line breaks as necessary
        max_chars_per_line = 30
        char_counter = 0
        while(len(raw_caption_queue) > 0):
            split = raw_caption_queue.split(' ')
            if(char_counter + len(split[0]) + 1 < max_chars_per_line):
                caption += " "
                char_counter += 1
            else:
                caption += "\n"
                char_counter = 0
            caption += split[0]
            char_counter += len(split[0])
            raw_caption_queue = " ".join(split[1:])
            
        txt_clip = TextClip(caption, fontsize=48, font=font, color='white', size=(width, height - img_clip.h))
        txt_clip = txt_clip.set_position(('center', 1-float(height-img_clip.h)/float(height)), relative=True).set_duration(duration)

        video = CompositeVideoClip([bg, img_clip, txt_clip])
        video = video.set_fps(24)
        dialogue_clips.append(video)

    final_clip = concatenate_videoclips(dialogue_clips)
    final_clip.write_videofile(output_path)
