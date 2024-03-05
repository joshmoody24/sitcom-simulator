def create_sitcom(
        prompt: str | None = None,
        art_style: str | None = None,
        script_path: str | None = None,
        debug_images: bool=False,
        debug_audio: bool=False,
        font: str = 'Arial',
        max_tokens:int=2048,
        approve_script:bool=False,
        manual_select_characters:bool=True,
        upload_to_yt=False,
        audio_job_delay:int=30,
        audio_poll_delay:int=10,
        caption_bg_style:str="box_shadow",
        save_script:bool=False,
        speed:float=1,
        pan_and_zoom:bool=True,
        orientation:str="portrait",
        resolution:int=1080,
        narrator_dropout:bool=False,
        music_url:str|None=None,
): 
    """
    Generates a sitcom video based on a prompt or a script file.
    It combines the script generation, voice generation, image generation, music generation, and video rendering steps into a single function.

    :param prompt: The prompt to generate the video script. If not provided, a script path must be provided.
    :param art_style: The art style to use for the video. If not provided, the art style will be selected by the language model.
    :param script_path: The path to a TOML script file to use for the video. The TOML must map to the Script model. If not provided, a prompt must be provided.
    :param debug: If True, the video will be generated using the debug mode, which uses the GTTS and Pillow engines instead of the FakeYou and Stability engines to increase speed and reduce costs.
    :param font: The font to use for the video. This font must be installed on the system.
    :param max_tokens: The maximum number of tokens to use for the language model. This will affect the length of the generated script.
    :param approve_script: If True, the script must be approved by the user before generating the video.
    :param manual_select_characters: If True, the user will be prompted to select the characters for the video. If False, the characters will be selected automatically by the language model.
    :param upload_to_yt: If True, the video will be uploaded to YouTube after it is generated. NOTE: currently does not work.
    :param audio_job_delay: The number of seconds to wait between starting audio generation jobs. Lower values render faster but are more likely to get rate limited. (FakeYou only)
    :param audio_poll_delay: The number of seconds to wait between polling for audio generation job completion. (FakeYou only)
    :param caption_bg_style: The style of the background behind the captions.
    :param save_script: If True, the generated script will be saved to a file.
    :param speed: The speed of the final video. 1.0 is normal speed.
    :param pan_and_zoom: If True, the pan and zoom effect on images will be enabled.
    :param orientation: The orientation of the video. "landscape", "portrait", or "square".
    :param resolution: The width of the video to render assuming portrait mode. This takes into account the orientation parameter.
    :param narrator_dropout: If True, the narrator will be forcibly removed from the script (ChatGPT often goes heavy on the narrators).
    :param music_url: A URL to a music track to use for the video.
    """
    from .models import VideoResult
    from .script import write_script
    from .speech import add_voices
    from .image import add_images
    from .music import add_music
    from .video import render_video
    from .script import script_from_file
    from .social.yt_uploader import upload_to_yt
    
    if(prompt == None and script_path == None):
        prompt = input("Enter a prompt to generate the video script: ")

    assert prompt or script_path, "You must provide a prompt or a script path"
    assert orientation in ["landscape", "portrait", "square"], "Orientation must be 'landscape', 'portrait', or 'square'"

    if prompt and not script_path:
        initial_script = write_script(
            prompt=prompt,
            manual_character_selection=manual_select_characters,
            max_tokens=max_tokens,
            require_approval=approve_script,
            fakeyou_characters=not debug_audio,
            narrator_dropout=narrator_dropout,
        )
    elif script_path and not prompt:
        initial_script = script_from_file(script_path)
    else:
        raise ValueError("You must provide a prompt or a script path, not both")
    
    if art_style:
        initial_script = initial_script.replace(metadata=initial_script.metadata.replace(art_style=art_style))

    script_with_voices = add_voices(
        initial_script,
        engine="fakeyou" if not debug_audio else "gtts",
        fakeyou_job_delay=audio_job_delay,
        fakeyou_poll_delay=audio_poll_delay,
    )

    # image gen could theoretically be done in parallel with the audio
    script_with_images = add_images(
        script_with_voices,
        engine="stability" if not debug_images else "pillow",
        orientation=orientation,
    )
    
    script_with_music = add_music(
        script=script_with_images,
        music_url=music_url,
    )

    final_script = script_with_music

    filename = final_script.metadata.title[:50].strip() or 'render' if final_script.metadata.title else 'render'
    output_path = f"./{filename}.mp4"

    final_video_path = render_video(
        script=final_script,
        font=font,
        output_path=output_path,
        caption_bg_style=caption_bg_style,
        resolution=resolution,
        orientation=orientation,
        speed=speed,
        pan_and_zoom=pan_and_zoom,
    )

    result = VideoResult(
        path=final_video_path,
        title=final_script.metadata.title if final_script.metadata.title else filename,
        description=prompt or 'an AI-generated meme video created with Sitcom Simulator'
    )

    print(f"Video generated at {final_video_path}")

    if save_script:
        import toml
        from dataclasses import asdict
        with open(f"./{filename}.toml", 'w') as f:
            f.write(toml.dumps(asdict(final_script)))
        print(f"Script saved at ./{filename}.toml")

    # if upload_to_yt:
    #     title = prompt
    #     keywords = [word for word in prompt.split(' ') if len(word) > 3] if prompt else ["sitcom", "funny", "comedy", "ai", "deepfake"]
    #     upload_to_yt(result.path, result.title, result.description, keywords, "24", "public")

    return result