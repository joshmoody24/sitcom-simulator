from typing import Callable
from ..models import Script
import tomllib
from dataclasses import asdict
import logging

def write_script(
        prompt: str,
        manual_character_selection=False,
        max_tokens:int=2048,
        require_approval:bool=False,
        temperature:float=0.5,
        fakeyou_characters:bool=True,
        ) -> Script:
    """
    Uses AI to generate a script matching the prompt.
    
    If characters are passed in, the resulting dialog is constrained to those characters.
    Otherwise, it prompts the user to select the appropriate characters.

    :param prompt: The prompt for the script
    :param manual_character_selection: Whether to prompt the user to select the characters. If manual_character_selection == False and characters == None, an LLM will extract characters.
    :param max_tokens: The maximum number of tokens to generate
    :param require_approval: Whether to prompt the user to approve the generated script
    :param temperature: The temperature to use when generating the script
    :param fakeyou_characters: Whether to restrict character selection to only voices from fakeyou.com
    """
    from ..speech.integrations.fakeyou import get_possible_characters_from_prompt
    from .integrations.chatgpt import chatgpt, instructions
    from .integrations.fakeyou.character_extractor import generate_character_list
    from ..music.integrations.freepd import MusicCategory

    if manual_character_selection:
        from .integrations.fakeyou.character_selector import select_characters as fakeyou_select_characters
        from ..user_input import select_characters as debug_select_characters
        possible_characters = get_possible_characters_from_prompt(prompt)
        select_characters: Callable = fakeyou_select_characters if fakeyou_characters else debug_select_characters
        characters = select_characters(possible_characters)
    else:
        characters = generate_character_list(prompt)

    characters_str = ", ".join([c.name for c in characters])
    music_categories_str = ", ".join(MusicCategory.values())
    full_prompt = instructions.base_prompt.format(prompt=prompt, characters=characters_str, max_tokens=max_tokens, music_categories=music_categories_str)
    approved = False
    while not approved:
        raw_script= chatgpt.chat(full_prompt, temperature=temperature, max_tokens=max_tokens)
        toml_script = tomllib.loads(raw_script)
        toml_script["characters"] = [asdict(c) for c in characters] # from characters to dict back to character. Refactor at some point.
        script = Script.from_dict(toml_script)
        logging.debug(script)
        print(formatted_script(script))
        if(require_approval):
            validated = None
            while validated not in ["y", "n", "q"]:
                validated = input("Do you approve this script? (y/n/q): ").lower()
                if validated == "y": approved = True
                elif validated == "n": approved = False
                elif validated == "q": exit()
                else: print("Unrecognized input. Try again.")
        else:
            approved = True
    return script

def script_from_file(path: str) -> Script:
    with open(path, "rb") as f:
        script = Script.from_dict(tomllib.load(f))
        print(type(script))
        return script
    
def formatted_script(script: Script) -> str:
    metadata = f"Title: {script.metadata.title or '<No Title>'}\nStyle: {script.metadata.art_style or '<No Art Style>'}\n"
    clips = "\n".join([f"{c.speaker}: {c.speech}" for c in script.clips if c.speaker])
    return metadata + clips