# two modes - auto and manual

# start with auto

import os
import shutil
from dotenv import load_dotenv, find_dotenv
import random
from generators.scriptgenerator import generate_script, generate_description
from generators.imagegenerator import generate_prompts, generate_images, generate_image
from generators.audiogenerator import generate_voice_clips
from generators.moviegenerator import generate_movie
from utils.argparser import parse_args
from utils.fakeyou import get_characters_in_prompt
from utils.toml import load_toml
import sys
import glob

def create_sitcom(args):
    if(args.prompt == None and args.script == None):
        args.prompt = input("Please enter a prompt to generate the video script: ")

    # clean prompt
    prompt = args.prompt.replace('-', ' ')

    # load custom high-quality character data
    curated_characters = load_toml("./characters/characters.toml")

    print("--- Character Voice Selection ---")    
    # scan the prompt for character names
    possible_characters = get_characters_in_prompt(prompt)

    # if multiple matches, user chooses which voice to use
    selected_voices = {}
    for name, voices in possible_characters.items():
        print(f"\n\nCharacter detected in script: {name}\n")
        selection = None
        error = None
        while(selection == None):
            if(error):
                print(f"\nError: {error}\n")
            print("0. Do not include this character.")
            for i, voice in enumerate(voices):
                print(f"{i+1}. {voice['title']} by {voice['creator_display_name']}")
            print('')
            try:
                selection = int(input("Which voice do you want to use for this character? (number) "))
                if(selection > len(voices) or selection < 0):
                    selection = None
                    error = "Number out of range."
            except Exception:
                selection = None
                error = "Please enter a valid number."
        # go back to zero-indexing
        selection -= 1
        if(selection >= 0):
            selected_voices[name] = voices[selection]

    # the final list of charactesr
    # it won't have all the data yet
    # but it will have enough to generate the script
    characters = {}
    for i, name in enumerate(selected_voices):
        characters[name] = dict()
    # keep generating scripts until user approves
    while(True):
        lines = generate_script(f"A script for {args.prompt}", characters, args.max_length)
        # line['action'] is also a thing. Not being used at the moment. For example "Mario (running towards Luigi):"
        print("\nScript:\n", '\n'.join([f'{line["speaker"]}: {line["text"]}' for line in lines]))
        if(args.validate_script):
            validated = input("Do you approve this script? (y/n): ")
            if(validated.lower() == "y"):
                break
            else:
                continue
        else:
            break

    # user types visual descriptions for each character for stable diffusion
    character_descriptions = {}
    print("\n--- Image Prompt Descriptions ---\n")
    for name, voice in selected_voices.items():
        description = input(f"Please enter a visual description of [{name}] or leave blank to use their name: ({name}) ")
        if(description == None or description.strip() == ""):
            description = name
        character_descriptions[name] = description

    # convert data into correct format for rest of process
    for i, name in enumerate(selected_voices):
        characters[name]['description'] = character_descriptions[name]
        characters[name]['voice_token'] = selected_voices[name]['model_token']


    prompts = generate_prompts(lines, characters, args.style)
    audio_extension = "wav" if args.high_quality_audio else "mp3"
    generate_voice_clips(lines, args.high_quality_audio)
    generate_images(prompts, args.img_quality)
    movieData = []
    # sort the image files by create date to get them in order
    images = glob.glob('./tmp/*.png')
    print(images)
    images.sort(key=os.path.getmtime, reverse=True)
    print(images)
    for i in range(len(lines)):
        data = {
            'caption': lines[i]["text"],
            'image': images[i],
            'audio': f"./tmp/{i+1}.{audio_extension}"
        }
        movieData.append(data)

    video_title = prompt
    if(not os.path.exists(f'./renders/{video_title}')):
        os.makedirs(f'./renders/{video_title}')
    generate_movie(movieData, f"./renders/{video_title}/{video_title}.mp4")

    # clean the tmp folder 
    shutil.rmtree('./tmp')

    # all the commented sections below are auto-generated YouTube thumbnails and descriptions
    # it works, but the youtube api restricts videos,
    # so I've temporarily disabled this functionality
    # while figuring out a better system

    # generate description
    # temporarily disabled
    # description = generate_description(video_title)
    # yt forces the video to be private. Looking into it.
    # upload_to_yt(f"./renders/{video_title}.mp4", video_title, description, keywords, privacyStatus="public")
    # file1 = open(f"./renders/{video_title}/description.txt", "w")  # append mode
    # file1.write(description)
    # file1.close()

    # generate thumbnail for youtube
    # temporarily disabled
    # generate_image(f'{video_title} youtube centered clickbait', f'./renders/{video_title}/thumbnail', quality=args.img_quality, width=512, height=512)


if(__name__ == "__main__"):
    print("\nSitcom Simulator\nBy Josh Moody\n")

    # load environment variables from .env file
    load_dotenv(find_dotenv())

    # process command line arguments
    args = parse_args()
    print(os.environ.get("OPENAI_KEY"))

    # do the magic
    create_sitcom(args)