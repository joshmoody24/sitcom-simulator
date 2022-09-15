from moviepy.editor import *

# example input
'''
[{
    caption='Itsa me, Mario',
    image=./path/to/image,
    audio=./path/to/audio
}]
'''
def generate_movie(dialogueData=[{}]):
    dialogue_clips = []
    for dialogue in dialogueData:

        voiceover = AudioFileClip(dialogue['audio'])

        # calculate the duration
        hang_time = 0.35
        duration = voiceover.duration + hang_time
        if(duration < 2):
            duration = 2

        # black background
        bg = ColorClip(size=(1280,720), color=[0,0,0])
        bg = bg.set_duration(duration)
        bg = bg.set_audio(voiceover)

        # the image
        img_clip = ImageClip(dialogue['image'])
        img_clip = img_clip.set_duration(duration)
        img_clip = img_clip.set_fps(24)
        img_clip = img_clip.set_position(('center', 'top'))

        # the caption
        raw_caption = dialogue["caption"]
        raw_caption_queue = raw_caption
        caption = ""
        # generate line breaks as necessary
        max_chars_per_line = 54
        char_counter = 0
        while(len(raw_caption_queue) > 0):
            split = raw_caption_queue.split(' ')
            caption += split[0]
            char_counter += len(split[0])
            if(char_counter < max_chars_per_line):
                caption += " "
            else:
                caption += "\n"
                char_counter = 0
            raw_caption_queue = " ".join(split[1:])
        txt_clip = TextClip(caption, fontsize=30, color='white')
        txt_clip = txt_clip.set_position(('center', 0.8), relative=True).set_duration(duration)

        video = CompositeVideoClip([bg, img_clip, txt_clip])
        video = video.set_fps(24)
        dialogue_clips.append(video)

    final_clip = concatenate_videoclips(dialogue_clips)
    final_clip.write_videofile("test.mp4")

    # example code

    # Import everything needed to edit video clips

    # Load myHolidays.mp4 and select the subclip 00:00:50 - 00:00:60
    # clip = VideoFileClip("myHolidays.mp4").subclip(50,60)

    # Reduce the audio volume (volume x 0.8)
    # clip = clip.volumex(0.8)

    # Generate a text clip. You can customize the font, color, etc.
    # txt_clip = TextClip("My Holidays 2013",fontsize=70,color='white')

    # Say that you want it to appear 10s at the center of the screen
    # txt_clip = txt_clip.set_pos('center').set_duration(10)

    # Overlay the text clip on the first video clip
    # video = CompositeVideoClip([clip, txt_clip])

    # Write the result to a file (many options available !)
    # video.write_videofile("myHolidays_edited.webm")