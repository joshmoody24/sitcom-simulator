import tempfile
from gtts import gTTS
from typing import List
from ...models import Script
from tqdm import tqdm
from typing import Optional, Callable
import atexit
import os

def generate_voices(script: Script, on_voice_generated: Optional[Callable[[int, str], None]] = None) -> List[str | None]:        
    filepaths: List[str | None] = []
    for i, line in tqdm(enumerate(script.clips), "Generating voice clips", total=len(script.clips)):
        if not line.speech:
            filepaths.append(None)
            continue
        tts = gTTS(line.speech, lang="en")
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_file.name)
        atexit.register(os.remove, temp_file.name)
        filepaths.append(temp_file.name)
        if on_voice_generated:
            on_voice_generated(i, temp_file.name)
    return filepaths