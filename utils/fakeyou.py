import requests
def fetch_voicelist():
    response = requests.get('https://api.fakeyou.com/tts/list')
    json = response.json()
    if(json['success'] != True):
        print("Error fetching voice list from fakeyou. Exiting.")
        exit()
    return json['models']

def strip_voice_title(title):
    return title.split('(')[0].strip().replace('-', ' ')

def get_characters_in_prompt(prompt):
    possible_characters = dict()
    voices = fetch_voicelist()
    for voice in voices:
        # only check up to parenthesis
        # e.g. a voice titled "Mario (Mario 64)" should still match "Mario"
        stripped_voice = strip_voice_title(voice['title'])

        # if detailed_search == True
        # check each word of the voice, since a voice titled "Avatar Aang" would match prompt "Aang"
        # this is kind of jank so I'm turning it off for now
        detailed_search = False

        split_voice = [word for word in stripped_voice.split(' ') if len(word) > 3] if detailed_search else [stripped_voice]
        character_in_prompt = False
        for word in split_voice:
            if(word.lower() in prompt.lower()):
                character_in_prompt = True
                break
        if(character_in_prompt):
            if(stripped_voice in possible_characters):
                possible_characters[stripped_voice].append(voice)
            else:
                possible_characters[stripped_voice] = [voice]

    return possible_characters