from .integrations.script import chatgpt
from typing import List
from .integrations.tts.fakeyou import get_possible_characters_from_prompt
from .user_input import select_characters
from .integrations.music.freepd import MusicCategory

def generate_script(characters: List[dict] | None, args) -> dict:
    """Uses AI to generate a script matching the prompt.
    
    If characters are passed in, the resulting dialog is constrained to those characters.
    Otherwise, it prompts the user to select the appropriate characters unless full_auto is specified."""

    if not characters:
        possible_characters = get_possible_characters_from_prompt(args.prompt)
        characters = select_characters(possible_characters, high_quality_audio=args.high_quality_audio, full_auto=args.yes)

    # keep generating scripts until user approves
    approved = False
    while not approved:
        script = generate_script_draft(args.prompt, characters, args.max_tokens)
        # TODO: show the image_prompt in the validation
        print("\nScript:\n", '\n'.join([f'{line["character"]}: {line["speech"]}' for line in script['lines']]))
        if(args.validate_script):
            validated = None
            while validated not in ["y", "n", "q"]:
                validated = input("Do you approve this script? (y/n/q): ").lower()
                if validated == "y": approved = True
                elif validated == "n": approved = False
                elif validated == "q": exit()
                else: print("Unrecognized input. Try again.")
        else:
            break
    return script

def generate_script_draft(
        prompt: str,
        characters: List[dict],
        max_tokens: int,
        temperature: float=0.5,
        full_auto:bool=False,
        high_quality_audio:bool=False
        ) -> dict:

    def character_string(name, voice) -> str:
        return f"- {name} (voice_token = {voice if 'model_token' in voice else 'n/a'})"

    available_characters_str = "\n".join(character_string(name, voice) for name, voice in characters.items())

    chatgpt_prompt = f"""
    Write a ~{round((max_tokens * 0.8)/10)*10}-word script for a movie in which {prompt}.
    Your output should be TOML, with the following values. Each value is required unless specified to be optional.

    title (title of the video)
    description (youtube description for the video)
    global_image_style (the visual style for the AI-generated images in the video)
    bgm_category (genre of background music. Available categories are {", ".join(MusicCategory.values())})
    characters (list of characters with the following attributes)
    \t- name
    \t- default_image_prompt (default short visual prompt for the AI image generator)
    \t- voice_token (this is provided for you)
    lines (list of each line of dialog with the following attributes)
    \t- character (the name of the character talking)
    \t- speech (the words the character is saying)
    \t- image_prompt (an optional prompt for the AI image generator. Defaults to character default_image_prompt)

    Image prompts should only depict one character at a time, to make it easier for the AI image generator.

    Example:
    title = "Mario slaps Luigi with a breadstick"
    global_style = "photograph, in a living room from the sitcom how I met your mother (1993)"

    [[characters]]
    name = "Mario"
    default_image_prompt = "Mario with red cap and mustache"
    voice_token="TM:c7j599fz0pbg"

    [[characters]]
    name = "Luigi"
    default_image_prompt="Luigi with green cap and mustache"
    voice_token="TM:fp4fcyja6mk1"

    [[lines]]
    character="Mario"
    speech="Hey Luigi, think fast!"
    image_prompt="close up photo of Mario with red cap and mustache, swinging breadstick aggressively with evil smirk"

    [[lines]]
    character="Luigi"
    speech="Ouch, I think you broke my nose! What did you do that for?"
    image="dramatic photo of Luigi in green cap, clutching his nose with both hands, eyes squeezed shut in agony"

    ... etc.
    
    
    The characters at your disposal are:
    {available_characters_str}
    
    The provided character list is auto-generated and may contain innappropriate, irrelelvant, or duplicate characters.
    Please filter these out according to your best judgement."""
    
    # debug
    print("ChatGPT Prompt: ", chatgpt_prompt)

    return chatgpt.generate_script(chatgpt_prompt, temperature=temperature, max_tokens=max_tokens)