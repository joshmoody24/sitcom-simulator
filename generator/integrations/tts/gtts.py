from gtts import gTTS
from typing import List
from ...models import Line

def generate_voice_clips(lines: Line):        
    counter = 1
    for line in lines:
        print(line.speech)
        tts = gTTS(line.speech, lang="en")
        tts.save(f"./tmp/{counter}.mp3")
        counter += 1