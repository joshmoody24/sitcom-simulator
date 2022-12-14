import os
import shutil
import glob
from dotenv import load_dotenv, find_dotenv
from generators.imagegenerator import generate_prompts, generate_images
from generators.audiogenerator import generate_voice_clips
from generators.moviegenerator import generate_movie
from generators.scriptgenerator import generate_description
from utils.argparser import parse_args
from utils.fakeyou import get_characters_in_prompt
from utils.userinput import select_characters, create_script, describe_characters
from utils.toml import load_toml
from social.yt_uploader import upload_to_yt

def create_sitcom(args, config):
    # clean the tmp folder to make sure we're starting fresh
    if(os.path.exists(f'./tmp')):
        shutil.rmtree('./tmp')

    if(args.prompt == None and args.script == None):
        args.prompt = input("Enter a prompt to generate the video script: ")

    # if using an existing script file
    if(args.script):
        script = load_toml(args.script)
        args.style = script['global_style']
        args.prompt = script['title']
        characters = {data['name']: data for data in script['characters']}
        lines = []
        for line in script['lines']:
            lines.append({
                "speaker": line['speaker'],
                "text": line['speech'],
                "action": "",
                "custom_prompt": line['custom_prompt'] if 'custom_prompt' in line else None,
            })
        # visually describe the character for image generation
        character_descriptions = dict()
        for name, data in characters.items():
            character_descriptions[name] = data['description']

    # if generating a script with GPT-3
    else:
        # clean prompt
        prompt = args.prompt.replace('-', ' ')
        possible_characters = get_characters_in_prompt(prompt)
        characters = select_characters(possible_characters, args)
        if(len(characters) <= 0):
            print("No voices selected. Exiting.")
            exit()
        lines = create_script(characters, args)
        # visually describe the character for image generation
        character_descriptions = describe_characters(characters, args)

    # convert data into correct format for rest of process
    for i, name in enumerate(characters):
        characters[name]['description'] = character_descriptions[name]
        if(args.script):
            characters[name]['voice_token'] = characters[name]['voice_token'] if args.high_quality_audio else ''
        else:
            characters[name]['voice_token'] = characters[name]['model_token'] if args.high_quality_audio else ''

    # generate the prompts used to generate images with stable diffusion
    prompts = generate_prompts(lines, characters, args.style)

    # generating voice clips can take a LONG time if args.high_quality_audio == True
    # because of long delays to avoid API timeouts on FakeYou.com
    audio_extension = "wav" if args.high_quality_audio else "mp3"
    generate_voice_clips(lines, characters, args.high_quality_audio, config)

    # save generating images till last since it costs money
    # don't want to crash afterward
    generate_images(prompts, args.img_quality)

    # set up the filesystem to prepare for the movie generation
    movieData = []
    # sort the image files by create date to get them in order
    images = glob.glob('./tmp/*.png')
    images.sort(key=os.path.getmtime)
    for i in range(len(lines)):
        data = {
            'caption': lines[i]["text"],
            'image': images[i],
            'audio': f"./tmp/{i+1}.{audio_extension}"
        }
        movieData.append(data)

    filename = args.prompt
    if(len(filename) > 50):
        filename = filename[:50].strip()
    if(not os.path.exists(f'./renders/{filename}')):
        os.makedirs(f'./renders/{filename}')

    generate_movie(config['font'], movieData, f"./renders/{filename}/{filename}.mp4")

    # clean the tmp folder again
    shutil.rmtree('./tmp')

    return f"./renders/{filename}/{filename}.mp4"

if(__name__ == "__main__"):
    print("\nSitcom Simulator\nBy Josh Moody\n")

    load_dotenv(find_dotenv())
    args = parse_args()
    config = load_toml('config.toml')
    
    # do the magic
    video_path = create_sitcom(args, config)
    if(args.upload):
        title = args.prompt
        description = generate_description(title)
        keywords = [word for word in description.split() if len(word) > 3]
        upload_to_yt(video_path, title, description, keywords, "24", "public")