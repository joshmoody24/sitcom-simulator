from gtts import gTTS
from pydub import AudioSegment
import requests
import uuid
import time
from pathlib import Path

# takes in array of line models
def generate_voice_clips(lines, high_quality=False):
    if(high_quality):
        # start all the jobs
        job_tokens = []
        job_delay = 52
        for iteration, line in lines:
            print(f"starting voice job for line {iteration}")
            entropy = str(uuid.uuid4())
            print(entropy)
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            payload = {
                "uuid_idempotency_token": entropy,
                "tts_model_token": line["speaker"]["voice_token"],
                "inference_text": line["text"]
            }
            response = requests.post('https://api.fakeyou.com/tts/inference', headers=headers, json=payload)
            json = response.json()
            print("response recieved")
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
        for token in job_tokens:
            completed = False
            while(not completed):
                print("polling job: ", token)
                headers={
                    'Accept': 'application/json'
                }
                response = requests.get(f'https://api.fakeyou.com/tts/job/{token}', headers=headers)
                json = response.json()
                print(json)
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
            tts = gTTS(line["text"], lang="it")
            tts.save(f"./tmp/{counter}.mp3")
            counter += 1

def shift_pitch(audio):
    raw = AudioSegment.from_file("C:\\Users\\joshm\\OneDrive - BYU\\Documents\\Programming\\Stable Diffusion\\mario.mp3", format="mp3")
    octaves = 0.5
    new_sample_rate = int(raw.frame_rate * (2.0 ** octaves))

    pitch_shifted = raw._spawn(raw.raw_data, overrides={'frame_rate':new_sample_rate})
    pitch_shifted = pitch_shifted.set_frame_rate(44100)
    pitch_shifted.export("luigi.mp3", format="mp3")