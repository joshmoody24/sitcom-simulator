import tomllib

with open("./characters/characters.toml", "rb") as f:
    curated_characters = tomllib.load(f)

# user selects which auto-detected characters to include in the script
# (including their voices if generating high-quality audio)
def select_characters(possible_characters, high_quality_audio:bool=False, full_auto:bool=False) -> dict:
    if not full_auto:
        print("--- Character Voice Selection ---")
    selected_characters = dict()
    for name, voices in possible_characters.items():
        print(f"\nCharacter detected in script: {name}")
        # choose voice model (if high quality audio)
        if high_quality_audio:
            # default option if one exists
            default_voice_token = curated_characters[name]['default_voice'] if name in curated_characters else None
            default_voice_index = None
            if(default_voice_token):
                for i, voice in enumerate(voices):
                    if(voice['model_token'] == default_voice_token):
                        default_voice_index = i + 1

            selection = None if full_auto == False else default_voice_index
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
                
        # ask user if they want to include this character (if low quality audio)
        else:
            include_character = None if full_auto == False else 'y'
            while(include_character not in ['y', 'n']):
                include_character = input("Include this character? (y/n) ").lower()
            if(include_character == 'y'):
                selected_characters[name] = dict()

    assert len(selected_characters) > 0, "No voices selected. Exiting."
    return selected_characters

def describe_characters(characters, full_auto:bool=False):
    " get visual descriptions for each character from the user "

    if not full_auto:
        print("\n--- Image Prompt Descriptions ---\n")
    character_descriptions = {}
    for name, voice in characters.items():
        default = name if name not in curated_characters else curated_characters[name]['image_prompt']
        description = input(f"Enter a visual description of [{name}] or leave blank to use default: ({default}) ") if full_auto == False else default
        if(description == None or description.strip() == ""):
            description = default
        character_descriptions[name] = description
    return character_descriptions