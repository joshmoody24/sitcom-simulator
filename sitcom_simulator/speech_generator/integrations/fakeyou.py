import requests
from tqdm import tqdm
from typing import List, Set, Callable, Optional, Dict
import re
import os
import time
import uuid
from pathlib import Path
from ...models import Script
import logging
import random
from sitcom_simulator.script_generator.integrations.fakeyou.narrators import BACKUP_NARRATORS
import urllib
import tempfile
import atexit

JOB_DELAY = 20 # seconds
JOB_RANDOMNESS = 3 # +- this value, might help bypass rate limiting
POLL_DELAY = 8
POLL_RANDOMNESS = 1

def download_voice(url: str):
    """Downloads audio from a given URL and saves it to a temporary file."""
    logging.info("downloading audio:", url)
    temp_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    atexit.register(os.remove, temp_audio_file.name)
    try:
        with urllib.request.urlopen(url) as response, open(temp_audio_file.name, 'wb') as out_file:
            data = response.read()  # Read the content as bytes
            out_file.write(data)
        return temp_audio_file.name
    except urllib.error.HTTPError as e:
        # Handle HTTP errors
        raise Exception(f"Failed to download audio from URL: {url}. Status code: {e.code}")
    except urllib.error.URLError as e:
        # Handle URL errors (e.g., network issues)
        raise Exception(f"Failed to download audio from URL: {url}. Error: {e.reason}")

def fetch_voicelist():
    response = requests.get('https://api.fakeyou.com/tts/list')
    json = response.json()
    if(json['success'] != True):
        print("Error fetching voice list from fakeyou. Exiting.")
        exit()
    return json['models']

def string_to_keywords(string: str, stop_at_first_paren=False) -> Set[str]:
    # don't match anything after the first parenthesis
    func = alphanumeric_to_first_paren if stop_at_first_paren else alphanumeric
    return {keyword.lower() for keyword in func(string).split(' ') if len(keyword) > 3 and keyword.lower() not in ['test', 'model']}

def alphanumeric_to_first_paren(string: str) -> str:
    string = string.split('(')[0].strip().replace('-', ' ')
    return alphanumeric(string)

def alphanumeric(string: str):
    return re.sub(r'[^a-zA-Z0-9 ]', '', string)

# scan the prompt for character names
def get_possible_characters_from_prompt(prompt: str) -> dict:
    possible_characters: Dict[str, List[str]] = dict()
    voices = fetch_voicelist()
    prompt_keywords = string_to_keywords(prompt, False)
    for voice in tqdm(voices, desc="Searching for characters in prompt:"):
        title = voice['title']
        character_name = alphanumeric_to_first_paren(title)
        voice_keywords = string_to_keywords(title, True)

        if len(voice_keywords) == 0:
            continue

        # at least this fraction of the keywords in the character name have to be found in the prompt
        MATCH_THRESHOLD = 0.45
        if(len(voice_keywords.intersection(prompt_keywords)) / len(voice_keywords) >= MATCH_THRESHOLD):   
            if(character_name in possible_characters):
                possible_characters[character_name].append(voice)
            else:
                possible_characters[character_name] = [voice]

    return possible_characters

# takes in array of line models
def generate_voices(script: Script, on_voice_generated: Optional[Callable[[int, str], None]] = None) -> List[str | None]:
    audio_urls: List[str | None] = []
    for i, clip in tqdm(enumerate(script.clips), desc="Generating voices", total=len(script.clips)):
        # skip if doesn't need audio, or if audio already exists (audio should never already exist, but just in case)
        if not clip.speaker:
            audio_urls.append(None)
            continue
        logging.debug(f'Starting voice job {i} ({clip.speaker}: {clip.speaker})')
        try:
            character = next((character for character in script.characters if character.name == clip.speaker))
        except Exception as e: # probably because character not in characters list
            character = random.choice(BACKUP_NARRATORS)
        entropy = str(uuid.uuid4())
        voice_token = character.voice_token
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "uuid_idempotency_token": entropy,
            "tts_model_token": voice_token,
            "inference_text": clip.speech,
        }
        response = requests.post('https://api.fakeyou.com/tts/inference', headers=headers, json=payload)
        try:
            json = response.json()
        except:
            print(response.text)
            raise Exception("Failed to parse JSON from FakeYou API: " + response.text + " " + str(payload))
        success = json['success']
        if not success:
            raise Exception("Some sort of FakeYou API error occured", json)
            break
        job_token = json['inference_job_token']
        rand_job_delay = random.randrange(JOB_DELAY-JOB_RANDOMNESS, JOB_DELAY+JOB_RANDOMNESS)
    
        # poll the job until complete
        logging.debug(f'Polling voice job {i}')
        polling_start_time = time.time()
        total_poll_time = 0.0
        completed = False
        headers={
            'Accept': 'application/json'
        }
        while not completed:
            rand_delay = random.randrange(POLL_DELAY-POLL_RANDOMNESS, POLL_DELAY+POLL_RANDOMNESS)
            time.sleep(rand_delay)
            response = requests.get(f'https://api.fakeyou.com/tts/job/{job_token}', headers=headers)
            json = response.json()
            if(not json["success"]):
                print("Some sort of polling error occurred", json)
                break
            status = json["state"]["status"]
            if(status == "pending" or status == "started"):
                continue
            elif(status == "complete_success"):
                completed = True
                total_poll_time = time.time() - polling_start_time
                audio_path = json["state"]["maybe_public_bucket_wav_audio_path"]
                audio_url = f'https://storage.googleapis.com/vocodes-public{audio_path}'
                audio_urls.append(audio_url)
                if(on_voice_generated):
                    on_voice_generated(i, audio_url)
            else:
                raise Exception("job failed, aborting", json)
                break

        # sleep the remaining time before next job
        remaining_delay = max(0, rand_job_delay - total_poll_time)
        time.sleep(remaining_delay)
    return audio_urls