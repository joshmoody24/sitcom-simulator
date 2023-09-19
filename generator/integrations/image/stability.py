from stability_sdk.client import StabilityInference, process_artifacts_from_answers, open_images
from dotenv import load_dotenv
import os
from tqdm import tqdm
from typing import List
from ...models import Line

def generate_image(prompt: str, prefix: str, width=1024, height=1024):

    STABILITY_HOST = os.getenv("STABILITY_HOST", "grpc.stability.ai:443")
    STABILITY_KEY = os.getenv("STABILITY_KEY", "gibberish_api_key")

    # customize engine here if desired (default is newest)
    # i.e. engine='stable-diffusion-v1-5'
    stability_api = StabilityInference(
        STABILITY_HOST, STABILITY_KEY, verbose=True
    )

    answers = stability_api.generate(
        prompt=prompt,
        width=width,
        height=height,
        )
    
    artifacts = process_artifacts_from_answers(
        prefix=prefix, prompt=prompt, answers=answers, write=True, verbose=False
    )

    # no idea why the rest of this code is necessary but it doesn't generate images without it
    showimages = False
    if showimages:
        for artifact in open_images(artifacts, verbose=True):
            pass
    else:
        for artifact in artifacts:
            pass
