from dotenv import load_dotenv
load_dotenv()

import os
import shutil
import glob
from generator.models import Line, Character, SpeechClip
from generator.script_generator import generate_script
from generator.tts_generator import generate_voice_clips
from generator.image_generator import generate_images
from generator.movie_generator import generate_movie
from generator.music_generator import generate_music
from generator.integrations.music.freepd import MusicCategory
from utils.argparser import parse_args
from social.yt_uploader import upload_to_yt
import tomllib
from dataclasses import dataclass
import random

@dataclass
class VideoResult:
    path: str
    title: str
    description: str

def create_sitcom(args, config):
    # clean the tmp folder to make sure we're starting fresh
    if(os.path.exists(f'./tmp')):
        shutil.rmtree('./tmp')
    os.makedirs('./tmp')

    if(args.prompt == None and args.script == None):
        args.prompt = input("Enter a prompt to generate the video script: ")

    ai_script = not args.script
    if ai_script:
        script = generate_script(None, args)
    else:
        with open(args.script, "rb") as f: script = tomllib.load(f)

    # parse toml dict into objects
    args.style = script.get('global_image_style', '')
    args.prompt = script['title']

    characters = [Character(
        character['name'],
        voice_token=character['voice_token'],
        default_image_prompt=character['default_image_prompt']
    ) for character in script['characters']]

    def find_character(name: str):
        return next(filter(lambda character: character.name == name, characters))
    
    lines = [Line(
        character=find_character(line['character']),
        speech=line['speech'],
        image_prompt=line.get('image_prompt', None) or find_character(line['character']).default_image_prompt
    ) for line in script['lines']]

    audio_extension = "wav" if args.high_quality_audio else "mp3"
    generate_voice_clips(lines, characters, args.high_quality_audio and not args.debug, config)

    # save generating images till last since it costs money - don't want something else to crash afterward
    generate_images(lines=lines, quality=args.img_quality, global_style=args.style, debug=args.debug)

    # set up the filesystem to prepare for the movie generation
    movie_data = []

    # sort the image files by create date to get them in order
    images = glob.glob('./tmp/*.png')
    images.sort(key=os.path.getmtime)
    voiceovers =  [f"./tmp/{i+1}.{audio_extension}" for i in range(len(images))]
    movie_data = [SpeechClip(
        caption=line.speech,
        image=image,
        audio=voiceover,
    ) for line, image, voiceover in zip(lines, images, voiceovers)]

    filename = args.prompt[:50].strip()
    if(not os.path.exists(f'./renders/')):
        os.makedirs(f'./renders/')

    bgm = generate_music(script.get('bgm_category', None) or random.choice(MusicCategory.values()))
    generate_movie(movie_data, bgm, config['font'], f"./renders/{filename}.mp4")

    # clean the tmp folder again
    shutil.rmtree('./tmp')

    return VideoResult(
        path=f"./renders/{filename}/{filename}.mp4",
        title=script['title'],
        description=script.get('description', args.prompt),
    )

if(__name__ == "__main__"):
    print("\nSitcom Simulator\nBy Josh Moody\n")

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    args = parse_args()
    
    # do the magic
    result = create_sitcom(args, config)
    if(args.upload):
        title = args.prompt
        keywords = [word for word in result.description.split() if len(word) > 3]
        upload_to_yt(result.path, result.title, result.description, keywords, "24", "public")