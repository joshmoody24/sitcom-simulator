from moviepy.editor import *

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

def generate_movie(font, dialogueData=[{}], output_path="output.mp4"):
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
        bg = ColorClip(size=(VIDEO_WIDTH,VIDEO_HEIGHT), color=[0,0,0])
        bg = bg.set_duration(duration)
        bg = bg.set_audio(voiceover)

        # the image
        img_clip = ImageClip(dialogue['image'])
        img_clip = img_clip.resize(VIDEO_WIDTH/img_clip.w,VIDEO_HEIGHT/img_clip.h)
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
            
        txt_clip = TextClip(caption, fontsize=48, font=font, color='white', size=(VIDEO_WIDTH, VIDEO_HEIGHT - img_clip.h))
        txt_clip = txt_clip.set_position(('center', 1-float(VIDEO_HEIGHT-img_clip.h)/float(VIDEO_HEIGHT)), relative=True).set_duration(duration)

        video = CompositeVideoClip([bg, img_clip, txt_clip])
        video = video.set_fps(24)
        dialogue_clips.append(video)

    final_clip = concatenate_videoclips(dialogue_clips)
    final_clip.write_videofile(output_path)
