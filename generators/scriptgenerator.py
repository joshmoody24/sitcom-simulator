import requests
import os
import random
from tqdm import tqdm

default_max_tokens = 128

def generate_description(video_title):
    api_key = os.getenv("OPENAI_KEY")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    json = {
        "model": "text-davinci-002",
        "prompt": f"a youtube video description for a video titled \"{video_title}\"",
        "max_tokens": 256,
        "temperature": 1,
        "top_p": 1,
        "n": 1,
        "stream": False,
        "logprobs": None,
        "echo": False,
        "frequency_penalty": 0,
    }
    res = requests.post('https://api.openai.com/v1/completions', headers=headers, json=json)
    description = res.json()["choices"][0]['text'].strip()
    return description

def generate_line(script_so_far, next_speaker_name, max_tokens=default_max_tokens, temperature=1):
    prompt = script_so_far + next_speaker_name + ":"
    api_key = os.getenv("OPENAI_KEY")
    # you can require actions by adding ' (' to the prompt
    if(api_key == None):
        raise Exception("No OpenAI API key provided")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    json = {
        "model": "text-davinci-002",
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "top_p": 1,
        "n": 1,
        "stream": False,
        "logprobs": None,
        "echo": False,
        "frequency_penalty": 0,
        # generate until the next speaker to check for stop codes
        # update: using ":" didn't work very well so I'm back to newlines
        "stop": "\n",
    }
    next_line = requests.post('https://api.openai.com/v1/completions', headers=headers, json=json)
    raw_text = next_line.json()["choices"][0]['text']
    split = raw_text.strip().split('\n')
    result = split[0]
    # was the ai trying to continue the script?
    # print("length of split",len(split))
    # print("raw: ", "\n".join(split))
    # print(result)
    too_short = 2
    if(len(result) <= too_short):
        return None

    # remove parentheticals (TODO: include them somehow?)
    speech = result.strip().replace(')','(').split('(')
    if(len(speech) > 1):
        action = speech[0]
        print(action)
        speech = speech[1].strip()
    else:
        speech = speech[0]
        action = None

    return {
        "speaker": next_speaker_name,
        "text": speech,
        "action": action,
    }

# returns a list of objects with all the data needed for future steps
def generate_script(prompt, characters, max_lines, style="", max_tokens_per_line=default_max_tokens, temperature=1):
    if(max_tokens_per_line > 1024):
        max_tokens_per_line = 1024
    if(max_tokens_per_line < 4):
        max_tokens_per_line = 4

    lines = []

    for i in tqdm(range(max_lines), desc="Generating script"):
        script_so_far = prompt + "\n\n"
        for prev in lines:
            script_so_far += f'{prev["speaker"]}: {prev["text"]}\n'
        # randomly select next speaker
        prev_speaker_name = lines[-1]["speaker"] if len(lines) > 0 else ""
        next_speaker_candidates = [name for name in characters if name != prev_speaker_name]
        if(len(characters) == 1):
            next_speaker_candidates.append(prev_speaker_name)
        next_speaker = random.choice(next_speaker_candidates)
        line = generate_line(script_so_far, next_speaker, max_tokens_per_line)
        if(line is None):
            break
        else:
            lines.append(line)
    return lines

    print("script generation complete")
