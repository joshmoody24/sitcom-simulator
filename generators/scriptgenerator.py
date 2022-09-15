import requests
import os
import random

api_key = os.getenv("OPENAI_KEY")

default_max_tokens = 32

def generate_line(script_so_far, next_speaker, max_tokens=default_max_tokens, temperature=1):
    prompt = script_so_far + next_speaker["name"] + ":"
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
        "stop": "\n",
    }
    next_line = requests.post('https://api.openai.com/v1/completions', headers=headers, json=json)
    result = next_line.json()["choices"][0]['text']
    too_short = 3
    if(len(result) <= too_short):
        return None

    # remove parentheticals (TODO: include them somehow?)
    speech = result.strip().replace(')','(').split('(')
    if(len(speech) > 1):
        action = speech[0]
        speech = [1].strip()
    else:
        speech = speech[0]

    return {
        "speaker": next_speaker,
        "text": speech
    }

# returns a list of objects with all the data needed for future steps
def generate_script(prompt, characters, max_lines, style="", max_tokens_per_line=default_max_tokens, temperature=1):
    if(max_tokens_per_line > 1024):
        max_tokens_per_line = 1024
    if(max_tokens_per_line < 4):
        max_tokens_per_line = 4

    lines = []

    for i in range(max_lines):
        script_so_far = prompt + "\n\n"
        for prev in lines:
            script_so_far += f'{prev["speaker"]["name"]}: {prev["text"]}\n'
        # randomly select next speaker
        prev_speaker_id = lines[-1]["speaker"]["id"] if len(lines) > 0 else ""
        next_speaker_candidates = [char for char in characters if char["id"] != prev_speaker_id]
        next_speaker = random.choice(next_speaker_candidates)
        line = generate_line(script_so_far, next_speaker, max_tokens_per_line)
        if(line is None):
            break
        else:
            lines.append(line)
    print("script generated: ", [line["text"] for line in lines])
    return lines

    print("script generation complete")