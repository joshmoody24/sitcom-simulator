Installation
=============

``pip install sitcom-simulator``

Dependencies
------------

You will need the following dependencies before running Sitcom Simulator for the first time:

* `Python 3.11 <https://www.python.org>`_ or later
* `FFmpeg <https://ffmpeg.org/download.html>`_
* `Stability API key <htps://https://beta.dreamstudio.ai/membership?tab=apiKeys>`_
* `OpenAI API key </https://openai.com/api>`_

FFmpeg
^^^^^^

The ``ffmpeg`` command must be accessible on your machine. This will vary depending on your system, but you can install it from the `official FFmpeg download page <https://ffmpeg.org/download.html>`_ or various package managers, e.g., ``apt install ffmpeg`` on Debian/Ubuntu, ``brew install ffmpeg`` on Mac, etc.

Alternatively, instead of installing ffmpeg on your system, you can place the ``ffmpeg`` and ``ffprobe`` binaries in your project's root directory, which will work equally well.

Environment Variables
---------------------

This package requires API keys from OpenAI and Stability AI to be stored in environment variables.

How you set the environment variables will depend on your use case, as explained below.

Command Line
^^^^^^^^^^^^

Set the environments in the terminal:

Linux: ``export OPENAI_API_KEY=<value>``

Windows: ``set OPENAI_API_KEY=<value>``

Python Projects
^^^^^^^^^^^^^^^

Create a ``.env`` file in your project's root directory, with the following structure:

.. code-block:: bash

    STABILITY_API_KEY='your_key_here
    OPENAI_API_KEY='your_key_here

The ``.env`` file will be automatically detected by the program.

You're ready to make your first meme video!