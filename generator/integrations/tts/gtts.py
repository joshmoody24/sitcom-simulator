from gtts import gTTS
from typing import List
from ...models import Line
from tqdm import tqdm

def generate_voice_clips(lines: Line):        
    counter = 1
    for line in tqdm(lines, "Generating voice clips"):
        tts = gTTS(line.speech, lang="en")
        tts.save(f"./tmp/{counter}.mp3")
        counter += 1