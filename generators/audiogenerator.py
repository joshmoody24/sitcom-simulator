from gtts import gTTS
import requests
import uuid
import time
from pathlib import Path
from tqdm import tqdm

# takes in array of line models
def generate_voice_clips(lines, high_quality=False):
    if(high_quality):
        # start all the jobs
        job_tokens = []
        job_delay = 52
        for i in tqdm(range(len(lines)), desc="Starting voice jobs"):
            entropy = str(uuid.uuid4())
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            payload = {
                "uuid_idempotency_token": entropy,
                "tts_model_token": lines[i]["speaker"]["voice_token"],
                "inference_text": lines[i]["text"]
            }
            response = requests.post('https://api.fakeyou.com/tts/inference', headers=headers, json=payload)
            print("printing response debug",response.text,"status code", response.status_code, "payload",payload)
            json = response.json()
            success = json['success']
            if(not success):
                raise Exception("Some sort of API error occured", json)
                break
            job_token = json['inference_job_token']
            job_tokens.append(job_token)
            time.sleep(job_delay)
        
        # poll the jobs until al  are complete
        poll_delay = 12
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
