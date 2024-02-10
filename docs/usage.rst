Usage
=====

Sitcom Simulator is designed to be simple to use, but also supports extreme customizability for power users who know exactly what they want. Sitcom Simulator can be used from the command line or can be imported in Python scripts.

Command Line
------------

.. code-block:: bash
    
    sitcom-simulator --prompt "Elon Musk teleports a toaster into the ocean" --style "beautiful renaissance oil painting"

Python
------

Sitcom Simulator can also be imported in Python scripts:

.. code-block:: python

    from sitcom_simulator import create_sitcom

    # generate a short meme video and save it in the project folder
    create_sitcom(
        prompt="Mario hits Luigi with a stapler",
    )

Power users can fully customize the video creation process:

.. code-block:: python

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

Now you know how to use Sitcom Simulator!

Enjoy making terrible meme videos 🐢