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


conn = sqlite3.connect("sitcomcli.sqlite3")
cursor = conn.cursor()

# randomly select 2 characters from the database
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

max_lines = 2

scriptLines = generate_script(f"A script in which {char1['name']} and {char2['name']} have a discussion about {topic}", characters, max_lines)
prompts = generate_prompts(scriptLines)
high_quality_audio = False
audio_extension = "wav" if high_quality_audio else "mp3"
generate_voice_clips(scriptLines, high_quality_audio)
generate_images(prompts, 5)
'''
scriptData = generate_script(prompt, style.description, first_speaker, first_line, 256)

        script = Script.objects.create(
            title = title,
            prompt = prompt,
            style = style,
        )

        counter = 1
        for segment in scriptData:
            line = Line.objects.create(
                speaker = Character.objects.get(display_name__iexact=segment["character"]),
                script = script,
                order = counter,
                dialogue = segment["speech"]
            )
            counter += 1
        
        return redirect(viewScriptPageView, slug=script.slug)


    characters = Character.objects.all()
    styles = Style.objects.all()
    context = {
        'characters': characters,
        'styles': styles
    }
    '''