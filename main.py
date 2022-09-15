# two modes - auto and manual

# start with auto

import os

from dotenv import load_dotenv
dotenv_path = os.path.abspath('.env')
load_dotenv(dotenv_path)
load_dotenv()

import sqlite3
import random
from generators.scriptgenerator import generate_script
from generators.imagegenerator import generate_prompts, generate_images
from generators.audiogenerator import generate_voice_clips
from generators.moviegenerator import generate_movie
import sys
from getopt import getopt

# parse cmd args
high_quality_audio = False
img_quality = 25
max_length = 10
require_validation = False
custom_prompt = None

argv = sys.argv[1:]
helptext = '''main.py
\tPARAMETERS:
\t-a [high quality audio flag]
\t-q <img-quality [5-50, default 25]>
\t-l <max_length [1-100, default 10]>
\t-v [require user validation for script]
\t-p \'<prompt>\''''
try:
    opts, args = getopt(argv, "vhaq:l:p:", ["hq-audio", "img-quality=", "max-length=","require-validation","prompt="])
except Exception as e:
    print(e,'\n',helptext)
    sys.exit(2)
for opt, arg in opts:
    print(opt)
    if(opt == '-h'):
        print(helptext)
        sys.exit(2)
    elif opt in ("-a", "--hq-audio"):
        high_quality_audio = True
    elif opt in ("-l", "--max-length"):
        max_length = int(arg)
        if(max_length > 100):
            max_length = 100
        elif(max_length < 1):
            max_length = 1
    elif opt in ("-q", "--img-quality"):
        img_quality = int(arg)
        if(img_quality > 50):
            img_quality = 50
        elif(img_quality < 5):
            img_quality = 5
    elif opt in ("-v", "--require-validation"):
        require_validation = True
    elif opt in ("-p", "--prompt"):
        custom_prompt = arg

conn = sqlite3.connect("sitcomcli.sqlite3")
cursor = conn.cursor()

# randomly select 2 characters from the database
if(not custom_prompt):
    characterIds = [x[0] for x in cursor.execute("SELECT CharacterId FROM Characters").fetchall()]
    char1 = cursor.execute("SELECT CharacterId, FullName, Description, VoiceToken FROM Characters WHERE CharacterId = ?", [random.choice(characterIds)]).fetchone()
    char1 = {
        "id": char1[0],
        "name": char1[1],
        "description": char1[2],
        "voice_token": char1[3]
    }
    characterIds.remove(char1["id"])
    char2 = cursor.execute("SELECT CharacterId, FullName, Description, VoiceToken FROM Characters WHERE CharacterId = ?", [random.choice(characterIds)]).fetchone()
    char2 = {
        "id": char2[0],
        "name": char2[1],
        "description": char2[2],
        "voice_token": char2[3]
    }
    characters = [char1, char2]

    topics = [row[0] for row in cursor.execute("SELECT Name FROM Topics").fetchall()]
    topic = random.choice(topics)

    video_title = f"{char1['name']} and {char2['name']} have a discussion about {topic}"
# custom prompt
else:
    # scan the prompt for character names
    characters_in_prompt = cursor.execute("SELECT CharacterId, FullName, Description, VoiceToken FROM Characters WHERE INSTR(LOWER(?),LOWER(FullName))", [custom_prompt]).fetchall()
    video_title = custom_prompt
    characters = []
    for char in characters_in_prompt:
        characters.append({
            "id": char[0],
            "name": char[1],
            "description": char[2],
            "voice_token": char[3]
        })
    print(characters)
# keep generating scripts until user approves
while(True):
    lines = generate_script(f"A script in which {video_title}", characters, max_length)
    print("Script:\n", '\n'.join([f'{line["speaker"]["name"]}: ({line["action"]}) {line["text"]}' for line in lines]))
    if(require_validation):
        validated = input("Do you approve this script? (y/n): ")
        if(validated.lower() == "y"):
            break
        else:
            continue
    else:
        break

prompts = generate_prompts(lines)
audio_extension = "wav" if high_quality_audio else "mp3"
generate_voice_clips(lines, high_quality_audio)
generate_images(prompts, img_quality)
movieData = []
for i in range(len(lines)):
    data = {
        'caption': lines[i]["text"],
        'image': f"./tmp/{i+1}.png",
        'audio': f"./tmp/{i+1}.{audio_extension}"
    }
    movieData.append(data)
generate_movie(movieData, f"./renders/{video_title}.mp4")