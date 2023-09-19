# Sitcom Simulator
A command-line tool for generating bad movies using GPT-3, Stable Diffusion, FakeYou, and MoviePy

## Prerequisites
- Python 3
- Stability API key (get one [here](https://beta.dreamstudio.ai/membership?tab=apiKeys))
- OpenAI API key (get one [here](https://openai.com/api/))

## Getting Started
### Setup
1. Download the source code (`git clone` or download zip and extract)
2. Open a terminal window in the root folder of the project
3. Install the dependencies: `pip install -r requirements.txt`
4. Create a .env file in the root directory
5. Put the following text into the .env file, replacing the variables with your API keys and file paths:
```
OPENAI_KEY='openai api key goes here'
STABILITY_KEY='stability api key goes here'
```
5. (Optional) Make sure the font variable in `config.toml` is a font installed on your computer
6. You're all set to start making terrible movies!

### YouTube API Setup
Sitcom Simulator supports automated YouTube video uploads. The process for setting it up is a bit tricky, but here's a broad overview. I'll create a more in-depth tutorial if there's interest in that. Hit me up.
1. Install the Google APIs Client Library for Python: `pip install --upgrade google-api-python-client google-auth-oauthlib google-auth-httplib2 oauth2client`
2. In Google Cloud, create a new project that has access to the YouTube Data v3 API. Then download your client_secrets csv, name it `client_secrets.json` and put it in the `social` directory
3. Use the -u flag to upload the final result to YouTube (it will prompt you to log in)

### Usage
`python create_sitcom.py [-h] [-a] [-q IMG_QUALITY] [-t MAX_TOKENS] [-v] [-p PROMPT] [-s STYLE] [-y]`

After some processing time, the video will be saved in the `renders` folder in the project directory

#### Example Command
`python create_sitcom.py --prompt "Luigi tells Mario about his service in the Vietnam war" --high-quality-audio --img-quality 30 --max-tokens 2048 --validate-script --style "on the sitcom how I met your mother (1993)"`

#### Arguments
- -h, --help: view help message
- -a, --high-quality-audio: use high quality deepfake audio instead of Google text-to-speech (significantly increases generation time)
- -q N, --img-quality N: image quality for generated images (5-100)
- -t N, --max-tokens N: max number of tokens in generated script (token ~= 0.8 words)
- -v, --validate-script: require user to approve generated script before creating video
- -p PROMPT, --prompt PROMPT: the prompt for the script that gets send to GPT-3
- -s STYLE, --style STYLE: a string that gets appended to image generation to customize image style
- -f PATH, --script PATH: specify a custom script (TOML format) instead of generating one (see sample_script.toml)
- -y, --yes: answer prompts automatically with 'yes' or default value
- -u, --upload: upload the video to YouTube automatically

## How it Works
Sitcom Simulator is essentially duct tape that combines multiple different AI tools into one unholy abomination.
- ChatGPT generates the video script
- FakeYou generates voices for the characters
- Stable Diffusion generates images for the characters
- FFmpeg connects the images and voices into a movie

## Contributions
Want to help work on this project? I'm down! Feel free to contribute. Hit me up if you have any questions 😘