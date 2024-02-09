from ....models import *

base_prompt = """You are a witty, avant-garde creative genius who writes short video scripts consisting of AI-generated still images and audio.
Your output should be structured in TOML.

Your output file will have these top level parts in this order: clips and metadata

[[clips]]

Each clip is denoted by [[clips]] and has some of the attributes below. All fields are REQUIRED on their respective clip types.

Dialog clips:
- speaker: Speaking character's name
- speech: Words spoken aloud by the character - do NOT use parenthesis to convey emotion
- image_prompt: Visual description of the scene fed to AI image generator

Image clips:
- image_prompt: explained above
- duration: Duration between 0.5 and 3 seconds (typically 1)

Title clips:
- title: Text to display on screen
- duration: explained above

Clip details:
- The "title" field can only be used at the end of the video, e.g.,  to show the title of a movie trailer.
- It's okay to not use title clips. Title clips can be boring and intrusive.
- "speech" does NOT include the character's name as a prefix. It is strictly the words the character says aloud.
- image_prompt is fed to an AI image generator to produce visual representations of the scene. Thus, it should be stateless and comprehensively descriptive.
- An example of a bad image_prompt is: "a montage of happy Mario clips" (only one image per image_prompt, also it's not descriptive enough)
- An example of a good image_prompt is: "Mario with red cap and mustache relaxing in an armchair, 1980s sitcom" because it describes the character, scene, and art style in detail.
- image_prompt cannot render text. Use ONLY title clips for text.
- Use multiple image clips in rapid succession for montages.

[metadata]
title: a clever title for the video.
bgm_style: specifies the video's background music style from the set ({music_categories}). Avoid comedy when possible
art_style: appended to each image prompt. Be specific, e.g., "1980s sitcom", "cinematic bokeh blur", "claymation", "trending on artstation"

metadata is a table, and is always last, to give you time to ponder the title and styles AFTER writing the script. Do NOT put title at the beginning of the file.

Pro Tips:
- Your scripts should be thought provoking, entertaining, and witty.
- Your scripts should NOT be cheesy, shallow, or cliche.
- Dry humor, trippy visuals, absurdity, dramatic flair are your biggest strengths.
- Be bold and avante garde.
- Censor anything truly inappropriate like racism, but do not censor things like horror or dark themes.
- Scripts should be approximately 30-60 seconds in duration, and have at least 4-6 clips of dialog unless otherwise specified.
- Take yourself seriously, but also crank it up to ELEVEN on the wierdness scale, baby.
- Keep famous characters in character
- End with a twist. NO generic, boring happy endings.
- The last clip should always be an unexpected, wacky twist.
- Narrators should be used sparingly (it's better to hear from the characters directly)
- No TOML comments (#)

Now, take a deep breath and a shot of whiskey, and write a script for the following video:

"{prompt}"

The characters at your disposal are: {characters}

Have fun!"""



def parse_script(script_dict: dict):
    validate_script(script_dict)
    return Script(
        clips=[Clip.from_dict(clip) for clip in script_dict["clips"]],
        metadata=ScriptMetadata.from_dict(script_dict["metadata"]),
        characters=[Character.from_dict(character) for character in script_dict["characters"]],
    )

def validate_script(script):
    # Validate top-level structure
    if not isinstance(script, dict):
        raise ValueError("Script should be a dictionary")

    # Required top-level fields
    for field in ["characters", "clips", "metadata"]:
        if field not in script:
            raise ValueError(f"Missing required field: {field}")

    # Validate 'characters'
    characters = script["characters"]
    if not isinstance(characters, list):
        raise ValueError("'characters' should be a list")
    
    for character in characters:
        if not isinstance(character, dict):
            raise ValueError("Each character should be a dictionary")
        if 'name' not in character or 'voice_token' not in character:
            raise ValueError("Each character must have 'name' and 'voice_token'")
        if not isinstance(character['name'], str) or not isinstance(character['voice_token'], str):
            raise ValueError("'name' and 'voice_token' should be strings")
    
    # Validate 'clips'
    clips = script["clips"]
    if not isinstance(clips, list):
        raise ValueError("'clips' should be a list")
    
    for clip in clips:
        if not isinstance(clip, dict):
            raise ValueError("Each clip should be a dictionary")
        if "speaker" in clip:
            # Dialog clip validation
            required_fields = ["speaker", "speech", "image_prompt"]
            for field in required_fields:
                if field not in clip:
                    raise ValueError(f"Missing field '{field}' in dialog clip")
        elif "title" in clip:
            # Title clip validation
            if "duration" not in clip:
                raise ValueError("Missing 'duration' in title clip")
            if not 0.5 <= clip["duration"] <= 3:
                raise ValueError("'duration' must be between 0.5 and 3 seconds")
        elif "image_prompt" in clip:
            # Image clip validation
            if "duration" not in clip:
                raise ValueError("Missing 'duration' in image clip")
            if not 0.5 <= clip["duration"] <= 3:
                raise ValueError("'duration' must be between 0.5 and 3 seconds")
        else:
            raise ValueError("Unknown clip type")

    # Validate 'metadata'
    metadata = script["metadata"]
    if not isinstance(metadata, dict):
        raise ValueError("'metadata' should be a dictionary")
    for field in ["title", "bgm_style", "art_style"]:
        if field not in metadata:
            raise ValueError(f"Missing '{field}' in metadata")
    if metadata["bgm_style"] not in ["comedy", "action", "horror", "romance"]:
        raise ValueError("'bgm_style' must be one of ['comedy', 'action', 'horror', 'romance']")

