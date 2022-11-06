import os
import shutil
import glob
from dotenv import load_dotenv, find_dotenv
from generators.imagegenerator import generate_prompts, generate_images, generate_image
from generators.audiogenerator import generate_voice_clips
from generators.moviegenerator import generate_movie
from utils.argparser import parse_args
from utils.fakeyou import get_characters_in_prompt
from utils.userinput import select_characters, create_script, describe_characters

def create_sitcom(args):
    # clean the tmp folder to make sure we're starting fresh
    shutil.rmtree('./tmp')

    if(args.prompt == None and args.script == None):
        args.prompt = input("Enter a prompt to generate the video script: ")

    # clean prompt
    prompt = args.prompt.replace('-', ' ')

    possible_characters = get_characters_in_prompt(prompt)
    characters = select_characters(possible_characters, args)
    if(len(characters) <= 0):
        print("No voices selected. Exiting.")
        exit()

    # visually describe the character for image generation
    character_descriptions = describe_characters(characters, args)

    # generate the script for the video
    lines = create_script(characters, args)

    # convert data into correct format for rest of process
    for i, name in enumerate(characters):
        characters[name]['description'] = character_descriptions[name]
        characters[name]['voice_token'] = characters[name]['model_token'] if args.high_quality_audio else ''

    # generate the prompts used to generate images with stable diffusion
    prompts = generate_prompts(lines, characters, args.style)

    # generating voice clips can take a LONG time if args.high_quality_audio == True
    # because of long delays to avoid API timeouts on FakeYou.com
    audio_extension = "wav" if args.high_quality_audio else "mp3"
    generate_voice_clips(lines, characters, args.high_quality_audio)

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

    if(not os.path.exists(f'./renders/{prompt}')):
        os.makedirs(f'./renders/{prompt}')

    generate_movie(movieData, f"./renders/{prompt}/{prompt}.mp4")

    # clean the tmp folder again
    shutil.rmtree('./tmp')

if(__name__ == "__main__"):
    print("\nSitcom Simulator\nBy Josh Moody\n")

    load_dotenv(find_dotenv())
    args = parse_args()
    
    # do the magic
    create_sitcom(args)