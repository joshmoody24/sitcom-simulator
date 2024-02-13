import json
import re
import random
from .narrators import BACKUP_NARRATORS
from sitcom_simulator.models import Character
import logging
from typing import List

def generate_character_list(prompt: str) -> List[Character]:
    """
    Uses a large language model to generate a list of possible famous characters related to the prompt.

    :param prompt: The user-submitted prompt
    """
    
    instructions = f"""Generate a list of potential characters to use in a short video of this prompt:

    {prompt}
    
    Your results will be searched for in the FakeYou database for potential AI voices to use.
    The characters must be likely to have an AI voice on the internet somewhere.
    Keep the list short and focused.
    Structure your output as a JSON list of strings.
    """
    from sitcom_simulator.script.llm import chat
    import requests
    
    raw_response = chat(instructions)
    character_names = json.loads(raw_response)
    print("Characters proposed:", ", ".join(character_names))
    
    # TODO: cache data from fakeyou to avoid lots of hits?
    res = requests.get('https://api.fakeyou.com/tts/list')
    fakeyou_character_list = res.json()['models']
    name_to_model = pure_name_to_model(fakeyou_character_list)
    
    chosen_characters = []
    for name in character_names:
        # TODO (big maybe) if tts doesn't exist but vtv does, render tts in someone else's voice and then use vtv
        if name.lower() not in name_to_model:
            continue
        matches = name_to_model[name.lower()]
        # find the highest-rated match
        highest_rated_voice = max(matches, key=calculate_star_rating)
        chosen_characters.append(Character(name=name, voice_token=highest_rated_voice['model_token']))
    logging.info("Selected voices:", ", ".join([c.name for c in chosen_characters]))
    
    # guarantee at least one voice (narrator)
    chosen_characters.append(random.choice(BACKUP_NARRATORS))
        
    return chosen_characters
        
def pure_name_to_model(models_list: list[dict]):
    """
    Given a list of models from FakeYou, returns a dictionary mapping the pure name of the character to the list of models matching that name.

    A pure name is the name of the character without any parenthetical information, e.g., "Velma (Scooby Doo)" -> "Velma"

    :param models_list: A list of models from FakeYou
    """
    names_to_model = {}
    for model in models_list:
        pure_name = pure_character_name(model['title'])
        if not pure_name:
            continue
        pure_name = pure_name.lower()
        if pure_name not in names_to_model:
            names_to_model[pure_name] = []
        names_to_model[pure_name].append(model)
    return names_to_model
        
NAME_PATTERN = re.compile(r"^\s*([^\(\n]*[^\s\(])\s*(?:\([^\n]*)?$")
def pure_character_name(raw_name: str):
    """
    Returns just the character's true name from a FakeYou listing.
    
    FakeYou names are typically formatted like \"True Name (source)\" e.g., Velma (Scooby Doo)
    
    :param raw_name: The raw name of the character from FakeYou
    """
    match = NAME_PATTERN.search(raw_name)
    if match:
        return match.group(1)
    return None
    
DEFAULT_RATING = 2 # not the worst possible, but pretty bad
def calculate_star_rating(model):
    """
    Estimates the true ratio of positive to negative reviews. Intuition: 5 stars from 10 reviews is worse than 4.8 stars from 1000 reviews.
    """
    
    if 'user_ratings' not in model: return DEFAULT_RATING
    positive_count = model['user_ratings']['positive_count']
    total_count = model['user_ratings']['total_count']
    
    negative_count = total_count - positive_count
    alpha_posterior = 1 + positive_count  # Prior alpha = 1
    beta_posterior = 1 + negative_count  # Prior beta = 1
    mean_proportion = alpha_posterior / (alpha_posterior + beta_posterior)
    star_rating = 1 + 4 * mean_proportion
    return mean_proportion, star_rating