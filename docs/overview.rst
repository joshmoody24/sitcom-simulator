Overview
================

What is Sitcom Simulator?
-----------------------------

Sitcom Simulator is a tool for auto-generating meme videos from text prompts.
The user enters a prompt, say, ``Mario and Luigi summon a demon``,
and the program generates a short video on that topic.

Sitcom Simulator design is focused on the following goals:

* **Ease of use**: The user should be able to generate a video with minimal effort.
* **Customization**: The user should be able to customize the video extensively.
* **Quality**: The user should be able to generate a video that is at least somewhat entertaining.
* **Speed**: The user should be able to generate a video within a few minutes.
* **Cost-effectiveness**: The user should be able to generate a video for pennies at most.

How does it work?
-----------------------------

Sitcom Simulator is essentially duct tape that combines multiple different AI tools into one unholy abomination.

#. `ChatGPT <https://chat.openai.com/>`_ generates the video script
#. `FakeYou <https://fakeyou.com>`_ generates voices for the characters
#. `Stable Diffusion <https://stability.ai/stable-image>`_ generates images for the characters
#. `Freepd <https://freepd.com/>`_ provides the background music
#. `FFmpeg <https://ffmpeg.org/>`_ connects the images and voices into a movie

Sitcom Simulator is available as a command line tool or as a python module. Continue following the documentation to learn how to use install and use it.