from sitcom_simulator.models import Character

def select_characters(possible_characters: dict[str, list[str]]):
    """
    Generic character selection procedure in which the user
    selects which auto-detected characters to include in the script.

    This function is currently unused since FakeYou has its own character selection procedure.

    :param possible_characters: A dictionary of character names to a list of voice tokens
    """
    print("--- Character Voice Selection ---")
    selected_characters = dict()
    for name, voices in possible_characters.items():
        print(f"\nCharacter detected in script: {name}")  
        include_character = None
        while(include_character not in ['y', 'n']):
            include_character = input("Include this character? (y/n) ").lower()
        if(include_character == 'y'):
            selected_characters[name] = dict()

    assert len(selected_characters) > 0, "No voices selected. Exiting."
    return [Character(name, voice) for name, voice in selected_characters.items()]

def describe_characters(characters: dict[str, str]):
    """
    A procedure to prompt the user to visually describe the characters in the script.

    This function is currently unused since the language model descriptions are used instead.

    :param characters: A dictionary of character names to voice tokens (although this should change to a list of Character objects in the future)
    """

    print("\n--- Image Prompt Descriptions ---\n")
    character_descriptions = {}
    for name, voice in characters.items():
        description = input(f"Enter a visual description of [{name}]: ")
        if(description == None or description.strip() == ""):
            description = "never gonna give you up rick astley" # gottem, lazy users >:D
        character_descriptions[name] = description
    return character_descriptions