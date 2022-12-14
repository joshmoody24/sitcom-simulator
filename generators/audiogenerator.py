from gtts import gTTS
import requests
import uuid
import time
from pathlib import Path
from tqdm import tqdm
import os

# takes in array of line models
def generate_voice_clips(lines, characters, high_quality=False, config=None):
    if(not os.path.exists('./tmp')):
        os.mkdir('./tmp')
    if(high_quality):
        # start all the jobs
        job_tokens = []
        job_delay = config['job_delay'] if 'job_delay' in config else 52
        for i in tqdm(range(len(lines)), desc="Starting voice jobs"):
            entropy = str(uuid.uuid4())
            voice_token = characters[lines[i]["speaker"]]["voice_token"]
            # basic-sounding microsoft cortana voice
            DEFAULT_VOICE = 'TM:5a3eejej7efk'
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            payload = {
                "uuid_idempotency_token": entropy,
                "tts_model_token": voice_token if voice_token else DEFAULT_VOICE,
                "inference_text": lines[i]["text"]
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
        poll_delay = config['poll_delay'] if 'poll_delay' in config else 12
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
                    raise Exception("job failed, aborting")
                    break

        # save to disk
        counter = 1
        for path in audio_urls:
            response = requests.get(f'https://storage.googleapis.com/vocodes-public{path}')
            filename = Path(f'./tmp/{counter}.wav')
            filename.write_bytes(response.content)
            counter += 1
            
    else:
        counter = 1
        for line in lines:
            tts = gTTS(line["text"], lang="en")
            tts.save(f"./tmp/{counter}.mp3")
            counter += 1
