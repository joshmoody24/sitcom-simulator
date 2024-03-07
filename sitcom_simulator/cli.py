from .auto import create_sitcom
import argparse

def _parse_args():
    parser = argparse.ArgumentParser(
        prog = "Sitcom Simulator",
        description = "A tool that creates bad sitcoms using AI tools",
        epilog = "Hit up the developer if you're having trouble 😘"
    )

    parser.add_argument('-t', '--max-tokens', metavar='N', type=int, default=2048, help="max number of tokens in generated script")
    parser.add_argument('-a', '--approve-script', action='store_true', help="require user to approve generated script before creating video")
    parser.add_argument('-p', '--prompt', type=str, help="the prompt for the script that gets send to ChatGPT")
    parser.add_argument('-s', '--style', type=str, help="a string that gets appended to image generation to customize image style")
    parser.add_argument('-f', '--script-path', metavar='PATH', type=str, help="use a custom TOML script file instead of generating one (see example script)")
    parser.add_argument('-u', '--upload', action="store_true", help="upload the generated video to YouTube")
    parser.add_argument('-m', '--manual-select-characters', action="store_true", help="manually select characters instead of using the AI to select them")
    parser.add_argument('-d', '--debug', action='store_true', help="skip expensive API calls, generating robotic TTS and blank images instead.")
    parser.add_argument('--debug-images', action='store_true', help="skip expensive image generation API calls, generating blank images instead.")
    parser.add_argument('--debug-audio', action='store_true', help="skip slow voice generation API calls, generating robotic TTS instead.")
    parser.add_argument('--font', type=str, help="the font to use for the video", default='Arial')
    parser.add_argument('--audio-job-delay', type=int, default=30, help="the number of seconds to wait between starting audio generation jobs. Lower values render faster but are more likely to get rate limited")
    parser.add_argument('--audio-poll-delay', type=int, default=10, help="the number of seconds to wait between polling for audio generation job completion")
    parser.add_argument('--text-shadow', action='store_true', help="use text shadow for captions instead of box background")
    parser.add_argument('--save-script', action='store_true', help="save the generated script to a file")
    parser.add_argument('--speed', type=float, default=1, help="speed up the final video by this factor (1.0 is normal speed)")
    parser.add_argument('--no-pan-and-zoom', action='store_true', help="disable pan and zoom effect on images")
    parser.add_argument('--resolution', type=int, default=1080, help="the resolution of the video (passing in 1080 means 1080p)")
    parser.add_argument('--orientation', type=str, default='portrait', help="the orientation of the video (landscape, portrait, or square)")
    parser.add_argument('--no-narrators', action='store_true', help="disable narrator characters")
    parser.add_argument('--music-url', type=str, help="a URL to a music track to use for the video")
    parser.add_argument('--audio-codec', type=str, help="the audio codec to use for the video: mp3 or aac", default='mp3')
    args = parser.parse_args()
    return args

def main():
    """
    The main entry point for the CLI, invoked when the module is run as a script.
    """
    print("\nSitcom Simulator\nBy Josh Moody\n")
    args = _parse_args()
    
    # do the magic
    create_sitcom(
        prompt=args.prompt,
        art_style=args.style,
        script_path=args.script_path,
        debug_images=args.debug_images or args.debug,
        debug_audio=args.debug_audio or args.debug,
        font=args.font,
        manual_select_characters=args.manual_select_characters,
        max_tokens=args.max_tokens,
        approve_script=args.approve_script,
        upload_to_yt=args.upload,
        audio_job_delay=args.audio_job_delay,
        audio_poll_delay=args.audio_poll_delay,
        caption_bg_style="text_shadow" if args.text_shadow else "box_shadow",
        save_script=args.save_script,
        speed=args.speed,
        pan_and_zoom=not args.no_pan_and_zoom,
        orientation=args.orientation,
        resolution=args.resolution,
        narrator_dropout=args.no_narrators,
        music_url=args.music_url,
        audio_codec=args.audio_codec,
    )