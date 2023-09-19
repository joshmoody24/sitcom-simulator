import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        prog = "Sitcom Simulator",
        description = "A tool that creates bad sitcoms using AI tools",
        epilog = "Hit up the developer if you're having trouble 😘"
    )

    parser.add_argument('-a', '--high-quality-audio', action='store_true', help="use high quality deepfake audio instead of Google text-to-speech (significantly increases generation time)")
    parser.add_argument('-q', '--img-quality', metavar='N', type=int, default=35, help="image quality for generated images (5-100)")
    parser.add_argument('-t', '--max-tokens', metavar='N', type=int, default=2048, help="max number of tokens in generated script")
    parser.add_argument('-v', '--validate-script', action='store_true', help="require user to approve generated script before creating video")
    parser.add_argument('-p', '--prompt', type=str, help="the prompt for the script that gets send to ChatGPT")
    parser.add_argument('-s', '--style', type=str, help="a string that gets appended to image generation to customize image style")
    parser.add_argument('-f', '--script', metavar='PATH', type=str, help="use a custom TOML script file instead of generating one (see example script)")
    parser.add_argument('-y', '--yes', action="store_true", help="answer prompts automatically with 'yes' or default value")
    parser.add_argument('-u', '--upload', action="store_true", help="upload the generated video to YouTube")

    args = parser.parse_args()
    return args