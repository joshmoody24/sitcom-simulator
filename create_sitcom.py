from dotenv import load_dotenv
load_dotenv()

import os
import shutil
import glob
from generator.models import Line, Character
from generator.script_generator import generate_script
from generator.audio_generator import generate_voice_clips
from generator.image_generator import generate_images
from generator.movie_generator import generate_movie
from utils.argparser import parse_args
from social.yt_uploader import upload_to_yt
import tomllib
from dataclasses import dataclass

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
    generate_voice_clips(lines, characters, args.high_quality_audio, config)

    # save generating images till last since it costs money
    # don't want to crash afterward
    generate_images(lines, args.img_quality, args.style)

    # set up the filesystem to prepare for the movie generation
    movie_data = []
    # sort the image files by create date to get them in order
    images = glob.glob('./tmp/*.png')
    images.sort(key=os.path.getmtime)
    for i in range(len(lines)):
        data = {
            'caption': lines[i].speech,
            'image': images[i],
            'audio': f"./tmp/{i+1}.{audio_extension}"
        }
        movie_data.append(data)

    filename = args.prompt
    if(len(filename) > 50):
        filename = filename[:50].strip()
    if(not os.path.exists(f'./renders/{filename}')):
        os.makedirs(f'./renders/{filename}')

    generate_movie(config['font'], movie_data, f"./renders/{filename}/{filename}.mp4")

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
        description = generate_description(title)
        keywords = [word for word in description.split() if len(word) > 3]
        upload_to_yt(result.path, result.title, result.description, keywords, "24", "public")