import requests
from tqdm import tqdm
from typing import List, Set
import re
import os
import time
import uuid
from pathlib import Path
from ...models import Line

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
    return {keyword.lower() for keyword in func(string).split(' ') if len(keyword) > 3}

def alphanumeric_to_first_paren(string: str) -> str:
    string = string.split('(')[0].strip().replace('-', ' ')
    return alphanumeric(string)

def alphanumeric(string: str):
    return re.sub(r'[^a-zA-Z0-9 ]', '', string)

# scan the prompt for character names
def get_possible_characters_from_prompt(prompt: str) -> List:
    possible_characters = dict()
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
def generate_voice_clips(lines: List[Line], characters, config=None):
    if(not os.path.exists('./tmp')):
        os.mkdir('./tmp')
    # start all the jobs
    job_tokens = []
    job_delay = config['job_delay'] if 'job_delay' in config else 52
    for i in tqdm(range(len(lines)), desc="Starting voice jobs"):
        entropy = str(uuid.uuid4())
        voice_token = lines[i].character.voice_token
        # basic-sounding microsoft cortana voice
        DEFAULT_VOICE = 'TM:5a3eejej7efk'
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {
            "uuid_idempotency_token": entropy,
            "tts_model_token": voice_token if voice_token else DEFAULT_VOICE,
            "inference_text": lines[i].speech
        }
        response = requests.post('https://api.fakeyou.com/tts/inference', headers=headers, json=payload)
        json = response.json()
        success = json['success']
        if(not success):
            raise Exception("Some sort of FakeYou API error occured", json)
            break
        job_token = json['inference_job_token']
        job_tokens.append(job_token)
        time.sleep(job_delay)
    
    # poll the jobs until all are complete
    poll_delay = config.get('poll_delay', 12)
    audio_urls = []
    for i in tqdm(range(len(job_tokens)), desc="Waiting for audio to render"):
        completed = False
        while(not completed):
            headers={
                'Accept': 'application/json'
            }
            response = requests.get(f'https://api.fakeyou.com/tts/job/{job_tokens[i]}', headers=headers)
            json = response.json()
            if(not json["success"]):
                print("Some sort of polling error occurred", json)
                break
            status = json["state"]["status"]
            if(status == "pending" or status == "started"):
                time.sleep(poll_delay)
                continue
            elif(status == "complete_success"):
                completed = True
                audio_urls.append(json["state"]["maybe_public_bucket_wav_audio_path"])
                time.sleep(poll_delay)
                continue
            else:
                raise Exception("job failed, aborting", json)
                break

    # save to disk
    counter = 1
    for path in audio_urls:
        response = requests.get(f'https://storage.googleapis.com/vocodes-public{path}')
        filename = Path(f'./tmp/{counter}.wav')
        filename.write_bytes(response.content)
        counter += 1