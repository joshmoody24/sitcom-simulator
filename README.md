# Sitcom Simulator
A highly-customizable tool that automatically creates AI-generated meme videos

`pip install sitcom-simulator`

## Examples

<p float="left">
    <a href="https://youtube.com/shorts/NQezju-_vtw?si=s2IcfYIhdK6oaE6o">
        <img src="https://joshmoody.org/sitcom-simulator/joe-biden-swole.png" width="200" />
    </a>
    <a href="https://youtube.com/shorts/QNAX7yAnEso?si=g6LtUvFu1_7VjjHJ">
        <img src="https://joshmoody.org/sitcom-simulator/mario-pyramid.png" width="200">
    </a>
    <a href="https://youtube.com/shorts/2JcaKnVGr8A?si=E9tg1SBv_VaHSVPo">
        <img src="https://joshmoody.org/sitcom-simulator/tom-cruise-mustard.png" width="200" />
    </a>
    <a href="https://youtube.com/shorts/7zKuojhaZz4?si=pFHuyQ4uX6j0B9FU">
        <img src="https://joshmoody.org/sitcom-simulator/fred-tax-fraud.png" width="200" />
    </a>
</p>
<p float="left">
    <a href="https://youtube.com/shorts/IFsYPP_g92I?si=nmy1OKl1jyuB8wa2">
        <img src="https://joshmoody.org/sitcom-simulator/dagoth-ur-trump.png" width="200" />
    </a>
    <a href="https://youtube.com/shorts/TAWfdZyrV68?si=2fn3mAEZKEi8TVc6">
        <img src="https://joshmoody.org/sitcom-simulator/iron-man-sonic.png" width="200" />
    </a>
    <a href="https://youtube.com/shorts/OpU1KsHHJuo?si=L90HAA7cHTYdB-VN">
        <img src="https://joshmoody.org/sitcom-simulator/shrek-donald-left-arm.png" width="200" />
    </a>
    <a href="https://youtube.com/shorts/KGtugZ4U7MA?si=cA6Uds3wOukBFeA4">
        <img src="https://joshmoody.org/sitcom-simulator/mario-cursed.png" width="200">
    </a>
</p>

And [several hundred more.](https://www.youtube.com/@SitcomSimulator/shorts)

## Features
- AI-generated scripts
- AI-generated images
- Deepfaked character voices
- Automatic background music finder
- Limitless customizability
- *(coming soon)* Automatic YouTube uploading

## Usage

Sitcom Simulator is designed to be simple to use, but also supports extreme customizability for power users who know exactly what they want. Sitcom Simulator can be used from the command line or can be imported in Python scripts.

### Command Line

The most basic usage is simply running the `sitcom-simulator` command with no arguments. Many optional arguments are supported as well. Note that you must [set your API key environment variables](#environment-variables) before it will work.

```bash
sitcom-simulator --prompt "Elon Musk teleports a toaster into the ocean" --style "beautiful renaissance oil painting" 
```

### Python

Sitcom Simulator can also be imported in Python scripts:

```python
from sitcom_simulator import create_sitcom

# generate a short meme video and save it in the project folder
create_sitcom(
    prompt="Mario hits Luigi with a stapler",
)
```

Power users can completely customize the video creation process:

```python
from sitcom_simulator import (
    script_from_file,
    add_voices,
    add_images,
    add_music,
    render_video,
)

def upload_to_s3(index, file_path):
    ... # arbitrary code

initial_script = script_from_file("custom_script.toml")

script_with_voices = add_voices(
    initial_script,
    engine="fakeyou",
    on_voice_generated=upload_to_s3)

script_with_images = add_images(
    script_with_voices,
    engine="stability",
    on_image_generated=upload_to_s3)

script_with_music = add_music(script_with_images)

render_video(
    script=final_script,
    font="Papyrus",
    output_path=f"./{final_script.metadata.title}.mp4")
```

More documentation on the advanced features will be coming soon.

## Getting Started

Several things must be completed before running Sitcom Simulator for the first time.

### Prerequisites
- Python 3
- [ffmpeg](https://ffmpeg.org/download.html) (see below for more details)
- Stability API key (get one [here](https://beta.dreamstudio.ai/membership?tab=apiKeys))
- OpenAI API key (get one [here](https://openai.com/api/))

#### FFmpeg

The ffmpeg command must be accessible on your machine. This will vary depending on your system, but you can install it from the [official download page](https://ffmpeg.org/download.html) or various package managers, e.g., `apt install ffmpeg` on Debian/Ubuntu, `brew install ffmpeg` on Mac, etc.

Alternatively, instead of installing ffmpeg on your system, you can place the `ffmpeg` and `ffprobe` binaries in your project's root directory, which will work equally well.

### Environment Variables

This package requires API keys from OpenAI and Stability AI to be stored in environment variables.

First, acquire API keys for OpenAI and Stability AI (see [prerequisites](#prerequisites))

How you set the environment variables will depend on your use case:

#### Comamnd Line

Set the environments in the terminal, i.e., `export OPENAI_API_KEY=<value>` (Linux) `set OPENAI_API_KEY=<value>` (Windows)

#### Python Projects

Create a `.env` file in your project's root directory, with the following structure:

```bash
STABILITY_API_KEY='your_key_here'
OPENAI_API_KEY='your_key_here'
```

The `.env` file will be automatically detected by the program.

## How it Works

Sitcom Simulator is essentially duct tape that combines multiple different AI tools into one unholy abomination.
1. [ChatGPT](https://chat.openai.com/) generates the video script
2. [FakeYou](https://fakeyou.com) generates voices for the characters
3. [Stable Diffusion](https://stability.ai/stable-image) generates images for the characters
4. [Freepd](https://freepd.com/) provides the background music
5. [FFmpeg](https://ffmpeg.org/) connects the images and voices into a movie

## Contributions

Want to help work on this project? I'm down! Feel free to reach out to me if you want to contribute or have any questions :)

Have fun!!!