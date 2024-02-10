import tomllib
from sitcom_simulator.models import Character
import os

# Get the directory of the current script file
script_dir = os.path.dirname(os.path.realpath(__file__))
characters_path = os.path.join(script_dir, 'characters.toml')
with open(characters_path, "rb") as f:
    curated_characters = tomllib.load(f)

# user selects which auto-detected characters to include in the script
# (including their voices if generating high-quality audio)
def select_characters(possible_characters: dict[str, list[str]]):
    """
    A procedure to prompt the user to select which auto-detected characters to include in the script.

    :param possible_characters: A dictionary of character names to a list of voice tokens
    """
    print("--- Character Voice Selection ---")
    selected_characters = dict()
    for name, voices in possible_characters.items():
        print(f"\nCharacter detected in script: {name}")
        # default option if one exists
        default_voice_token = curated_characters[name]['default_voice'] if name in curated_characters else None
        default_voice_index = None
        if(default_voice_token):
            for i, voice in enumerate(voices):
                if(voice['model_token'] == default_voice_token):
                    default_voice_index = i + 1

        selection = None
        error = None
            
        while(selection == None):
            if(error):
                print(f"\nError: {error}\n")
            print("\n0. Do not include this character.")
            for i, voice in enumerate(voices):
                line = f"{i+1}. {voice['title']} by {voice['creator_display_name']}"
                if(default_voice_index == i+1):
                    line += " (default)"
                print(line)
            print('')
            try:
                selection = int(input("Which voice do you want to use for this character? (number) "))
                if(selection > len(voices) or selection < 0):
                    selection = None
                    error = "Number out of range."
            except Exception:
                selection = None
                selection = default_voice_index if default_voice_index else 1
                print("Using the default voice for this character")
                
        # go back to zero-indexing
        selection -= 1
        if(selection >= 0):
            selected_characters[name] = voices[selection]

    assert len(selected_characters) > 0, "No voices selected. Exiting."
    return [Character(name, voice['model_token']) for name, voice in selected_characters.items()]