import tempfile
from typing import List
from ...models import Script
from tqdm import tqdm
from typing import Optional, Callable
import atexit
import os

def generate_voices(script: Script, on_voice_generated: Optional[Callable[[int, str], None]] = None) -> List[str | None]:
    """
    Generates and returns a list of voice clip paths for the given script using the Google Text-to-Speech API.
    Intended for debugging purposes and ironic memes only.

    :param script: The script to generate voice clips for
    :param on_voice_generated: A callback to call after each voice clip is generated which takes the clip index and path to the generated audio
    """      
    from gtts import gTTS
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