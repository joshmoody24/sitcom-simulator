import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        prog = "Sitcom Simulator",
        description = "A tool that creates bad sitcoms using AI tools",
        epilog = "Bottom text."
    )

    parser.add_argument('-a', '--high-quality-audio', action='store_true', help="use high quality deepfake audio instead of Google text-to-speech (significantly increases generation time)")
    parser.add_argument('-q', '--img-quality', type=int, default=25, help="image quality for generated images (5-100)")
    parser.add_argument('-l', '--max-length', type=int, default=10, help="max number of lines of dialogue in generated script")
    parser.add_argument('-v', '--validate-script', action='store_true', help="require user to approve generated script before creating video")
    parser.add_argument('-p', '--prompt', type=str, help="the prompt for the script that gets send to GPT-3")
    parser.add_argument('-s', '--style', type=str, help="a string that gets appended to image generation to customize image style")
    parser.add_argument('-f', '--script', type=str, help="use a custom TOML script file instead of generating one")
    parser.add_argument('-c', '--custom-voices', action="store_true", help="manually select voices instead of using the default for each character")

    args = parser.parse_args()
    return args