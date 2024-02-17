from .auto import create_sitcom
import argparse
import tomllib

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
    parser.add_argument('--font', type=str, help="the font to use for the video", default='Arial')
    parser.add_argument('--audio-job-delay', type=int, default=30, help="the number of seconds to wait between starting audio generation jobs. Lower values render faster but are more likely to get rate limited")
    parser.add_argument('--audio-poll-delay', type=int, default=10, help="the number of seconds to wait between polling for audio generation job completion")
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
        debug=args.debug,
        font=args.font,
        manual_select_characters=args.manual_select_characters,
        max_tokens=args.max_tokens,
        approve_script=args.approve_script,
        upload_to_yt=args.upload,
        audio_job_delay=args.audio_job_delay,
        audio_poll_delay=args.audio_poll_delay,
    )