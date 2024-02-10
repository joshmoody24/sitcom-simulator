from .models import Script, VideoResult
from .script_generator import write_script
from .speech_generator import add_voices
from .image_generator import add_images
from .music_generator import add_music
from .video_generator import render_video
from .script_generator import script_from_file
from .social.yt_uploader import upload_to_yt

def create_sitcom(
        prompt: str | None = None,
        art_style: str | None = None,
        script_path: str | None = None,
        debug: bool=False,
        font: str = '',
        max_tokens:int=2048,
        approve_script:bool=False,
        manual_select_characters:bool=True,
        upload_to_yt=False,
): 
    if(prompt == None and script_path == None):
        prompt = input("Enter a prompt to generate the video script: ")

    assert prompt or script_path, "You must provide a prompt or a script path"

    if prompt and not script_path:
        initial_script = write_script(
            prompt=prompt,
            manual_character_selection=manual_select_characters,
            max_tokens=max_tokens,
            require_approval=approve_script,
            fakeyou_characters=not debug,
        )
    elif script_path and not prompt:
        initial_script = script_from_file(script_path)
    else:
        raise ValueError("You must provide a prompt or a script path, not both")
    
    if art_style:
        initial_script = initial_script.replace(metadata=initial_script.metadata.replace(art_style=art_style))

    script_with_voices = add_voices(initial_script, engine="fakeyou" if not debug else "gtts")
    script_with_images = add_images(script_with_voices, engine="stability" if not debug else "pillow") # could theoretically be done in parallel with the audio
    script_with_music = add_music(script_with_images)

    final_script = script_with_music

    filename = final_script.metadata.title[:50].strip() or 'render'
    output_path = f"./{filename}.mp4"
    final_video_path = render_video(script=final_script, font=font, output_path=output_path)

    result = VideoResult(
        path=final_video_path,
        title=final_script.metadata.title,
        description=prompt or 'an AI-generated meme video created with Sitcom Simulator'
    )

    if upload_to_yt:
        title = prompt
        keywords = [word for word in prompt.split(' ') if len(word) > 3] if prompt else ["sitcom", "funny", "comedy", "ai", "deepfake"]
        upload_to_yt(result.path, result.title, result.description, keywords, "24", "public")

    return result