from typing import Callable
from ..models import Script
import toml
from dataclasses import asdict
import logging

def write_script(
        prompt: str,
        manual_character_selection=False,
        max_tokens:int=2048,
        require_approval:bool=False,
        temperature:float=0.5,
        model:str="gpt-3.5-turbo",
        custom_script_instructions: str | None=None,
        custom_character_instructions: str | None=None,
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
    :param model: The language model to use
    :param custom_script_instructions: A string containing custom instructions for the language model writing the script. Must contain the placeholders '{prompt}', '{music_categories}', and '{characters}'.
    :param custom_character_instructions: A string containing custom instructions for the language model extracting the characters from the prompt. Must contain the placeholder '{prompt}'.
    :param fakeyou_characters: Whether to restrict character selection to only voices from fakeyou.com
    """
    from ..speech.integrations.fakeyou import get_possible_characters_from_prompt
    from .integrations.chatgpt import chatgpt
    from .integrations.fakeyou.character_extractor import generate_character_list
    from ..music.integrations.freepd import MusicCategory

    if manual_character_selection:
        from .integrations.fakeyou.character_selector import select_characters as fakeyou_select_characters
        from ..user_input import select_characters as debug_select_characters
        possible_characters = get_possible_characters_from_prompt(prompt)
        select_characters: Callable = fakeyou_select_characters if fakeyou_characters else debug_select_characters
        characters = select_characters(possible_characters)
    else:
        characters = generate_character_list(prompt, custom_instructions=custom_character_instructions)

    characters_str = ", ".join([c.name for c in characters])
    music_categories_str = ", ".join(MusicCategory.values())

    if custom_script_instructions:
        instructions = custom_script_instructions
    else:
        from pathlib import Path
        current_file_path = Path(__file__).resolve()
        current_dir = current_file_path.parent
        instructions_path = current_dir / "llm_instructions.txt"
        with open(instructions_path, 'r') as f:
            instructions = f.read()
    
    # check for placeholders
    if "{prompt}" not in instructions or "{music_categories}" not in instructions or "{characters}" not in instructions:
        raise ValueError("Custom instructions file must contain the placeholders '{prompt}', '{music_categories}', and '{characters}'")

    full_prompt = instructions.format(prompt=prompt, characters=characters_str, max_tokens=max_tokens, music_categories=music_categories_str)
    approved = False
    while not approved:
        raw_script= chatgpt.chat(full_prompt, temperature=temperature, max_tokens=max_tokens, model=model)
        logging.debug("Raw script", raw_script)
        toml_script = toml.loads(raw_script)
        toml_script["characters"] = [asdict(c) for c in characters] # from characters to dict back to character. Refactor at some point.
        script = Script.from_dict(toml_script)
        logging.debug("TOML script", script)
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
    script = Script.from_dict(toml.load(path))
    return script
    
def formatted_script(script: Script) -> str:
    metadata = f"Title: {script.metadata.title or '<No Title>'}\nStyle: {script.metadata.art_style or '<No Art Style>'}\n"
    clips = "\n".join([f"{c.speaker}: {c.speech}" for c in script.clips if c.speaker])
    return metadata + clips