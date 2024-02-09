import tomllib
from utils.argparser import parse_args
from sitcom_simulator import create_sitcom

if(__name__ == "__main__"):
    print("\nSitcom Simulator\nBy Josh Moody\n")

    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    args = parse_args()
    
    # do the magic
    create_sitcom(
        prompt=args.prompt,
        style_override=args.style,
        script_path=args.script_path,
        debug=args.debug,
        font=config["font"],
        manual_select_characters=args.manual_select_characters,
        max_tokens=args.max_tokens,
    )