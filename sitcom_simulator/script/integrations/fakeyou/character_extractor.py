import json
import re
import random
from .narrators import BACKUP_NARRATORS
from sitcom_simulator.models import Character
import logging
from typing import List
import os
import csv

def load_curated_voices():
    """
    Loads the curated voices from the 'curated_voices.csv' file in the same directory as this script.
    Important for when fakeyou's ratings get wiped (which has happened before), we still have our own records.
    """
    curated_voices: dict[str, float] = {}
    # note: needs to be in the same directory as this script, not the current working directory
    path_to_curated_voices = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'curated_voices.csv')
    with open(path_to_curated_voices, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row['model_name'].strip()
            rating = row['rating'].strip()
            curated_voices[name] = float(rating)
    return curated_voices

def generate_character_list(prompt: str, custom_instructions: str | None=None) -> List[Character]:
    """
    Uses a large language model to generate a list of possible famous characters related to the prompt.

    :param prompt: The user-submitted prompt
    :param custom_instructions: A string containing custom instructions for the language model. Must contain the placeholder '{prompt}'.
    """


    if custom_instructions:
        instructions = custom_instructions
    else:
        from pathlib import Path
        current_file_path = Path(__file__).resolve()
        current_dir = current_file_path.parent
        instructions_path = current_dir / 'character_extraction_instructions.txt'
        with open(instructions_path, 'r') as f:
            instructions = f.read()

    if "{prompt}" not in instructions:
        raise ValueError("Custom instructions file must contain the placeholder '{prompt}'")
    instructions = instructions.format(prompt=prompt)

    from sitcom_simulator.script.llm import chat
    import requests
    
    raw_response = chat(instructions)
    logging.debug("Raw character extractor response from LLM:", raw_response)
    character_names = json.loads(raw_response)
    print("Characters proposed:", ", ".join(character_names))
    
    # TODO: cache data from fakeyou to avoid lots of hits?
    res = requests.get('https://api.fakeyou.com/tts/list')
    fakeyou_character_list = res.json()['models']
    name_to_model = pure_name_to_model(fakeyou_character_list)
    
    curated_characters = load_curated_voices()
    chosen_characters = []
    for name in character_names:
        # TODO (big maybe) if tts doesn't exist but vtv does, render tts in someone else's voice and then use vtv
        if name.lower() not in name_to_model:
            continue
        matches = name_to_model[name.lower()]
        # find the highest-rated match
        highest_rated_voice = max(matches, key=lambda model: calculate_star_rating(model, curated_characters))
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
def calculate_star_rating(model, curated_voices: dict[str, float] | None=None):
    """
    Estimates the true ratio of positive to negative reviews. Intuition: 5 stars from 10 reviews is worse than 4.8 stars from 1000 reviews.
    """

    curated_rating = curated_voices.get(model['title'])
    if curated_rating:
        return curated_rating
    
    if 'user_ratings' not in model: return DEFAULT_RATING
    positive_count = model['user_ratings']['positive_count']
    total_count = model['user_ratings']['total_count']
    
    negative_count = total_count - positive_count
    alpha_posterior = 1 + positive_count  # Prior alpha = 1
    beta_posterior = 1 + negative_count  # Prior beta = 1
    mean_proportion = alpha_posterior / (alpha_posterior + beta_posterior)
    star_rating = 1 + 4 * mean_proportion

    return star_rating