# Sitcom Simulator
A command-line tool for generating bad movies using ChatGPT, Stable Diffusion, FakeYou, and FFmpeg

## Prerequisites
- Python 3
- ffmpeg (see setup for more details)
- Stability API key (get one [here](https://beta.dreamstudio.ai/membership?tab=apiKeys))
- OpenAI API key (get one [here](https://openai.com/api/))

## Getting Started
### Setup
1. Download the source code (`git clone` or download zip and extract)
2. [Download FFmpeg](https://ffmpeg.org/download.html). The essentials build should work. Put the `ffmpeg` and `ffprobe` binaries in the project directory (same directory level as `create_sitcom.py`)
3. Open a terminal window in the root folder of the project
4. Install the dependencies: `pip install -r requirements.txt`
5. Create a `.env` file in the root directory
6. Put the following text into the `.env` file, replacing the variables with your API keys and file paths:
```bash
OPENAI_API_KEY='openai api key goes here'
STABILITY_API_KEY='stability api key goes here'
```
7. (Optional) Make sure the font variable in `config.toml` is a font installed on your computer
8. You're all set to start making terrible movies!

### YouTube API Setup (**not finished**)
Sitcom Simulator supports automated YouTube video uploads. The process for setting it up is a bit tricky, but here's a broad overview. I'll create a more in-depth tutorial if there's interest in that. Hit me up.
1. Install the Google APIs Client Library for Python: `pip install --upgrade google-api-python-client google-auth-oauthlib google-auth-httplib2 oauth2client`
2. In Google Cloud, create a new project that has access to the YouTube Data v3 API. Then download your client_secrets csv, name it `client_secrets.json` and put it in the `social` directory
3. Use the -u flag to upload the final result to YouTube (it will prompt you to log in)

### Usage
`python create_sitcom.py [-h] [-a] [-p PROMPT] [-s STYLE]`

After some processing time, the video will be saved to the project directory

#### Example Command
`python create_sitcom.py --prompt "Luigi tells Mario about his service in the Vietnam war" --max-tokens 2048 --approve-script --style "on the sitcom how I met your mother (1993)"`

#### Arguments
- -h, --help                        show this help message and exit
- -t N, --max-tokens N              max number of tokens in generated script
- -a, --approve-script              require user to approve generated script before creating video
- -p PROMPT, --prompt PROMPT        the prompt for the script that gets send to ChatGPT
- -s STYLE, --style STYLE           a string that gets appended to image generation to customize image style
- -f PATH, --script-path PATH       use a custom TOML script file instead of generating one (see example script)
- -u, --upload                      upload the generated video to YouTube
- -m, --manual-select-characters    manually select characters instead of using the AI to select them
- -d, --debug                       skip expensive API calls, generating robotic TTS and blank images instead.

## How it Works
Sitcom Simulator is essentially duct tape that combines multiple different AI tools into one unholy abomination.
- ChatGPT generates the video script
- FakeYou generates voices for the characters
- Stable Diffusion generates images for the characters
- FFmpeg connects the images and voices into a movie

## Contributions
Want to help work on this project? I'm down! Feel free to contribute. Hit me up if you have any questions 😘
