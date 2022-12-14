# sys.path.append('sitcoms\stabilitysdk\stability-sdk-main\src\stability_sdk')
from stability_sdk.client import StabilityInference, process_artifacts_from_answers, open_images, get_sampler_from_str
from dotenv import load_dotenv
import os
from tqdm import tqdm

def generate_prompts(lines, characters, style=None):
    prompts = []
    for line in lines:
        # randomSitcom = random.choice(RealLifeSitcom.objects.all())
        prompt = characters[line['speaker']]['description'] if ('custom_prompt' not in line or line['custom_prompt'] == None) else line['custom_prompt']
        if(style):
            prompt += f", {style}"
        prompts.append(prompt)
    return prompts

def generate_image(prompt, filename, quality=25, width=512, height=512):
    if(quality > 50):
        quality = 50
    if(quality < 5):
        quality = 5

    dotenv_path = os.path.abspath('.env')
    load_dotenv(dotenv_path)
    load_dotenv()
    STABILITY_HOST = os.getenv("STABILITY_HOST", "grpc.stability.ai:443")
    STABILITY_KEY = os.getenv("STABILITY_KEY", "")

    if not STABILITY_HOST:
        print("STABILITY_HOST environment variable needs to be set.")

    if not STABILITY_KEY:
        print(
            "STABILITY_KEY environment variable needs to be set. You may"
            " need to login to the Stability website to obtain the"
            " API key."
        )

    request = {
        "height": height,
        "width": width,
        "cfg_scale": 8,
        "sampler": get_sampler_from_str('k_lms'),
        "steps": quality,
    }

    stability_api = StabilityInference(
        STABILITY_HOST, STABILITY_KEY, engine='stable-diffusion-768-v2-1', verbose=True
    )

    answers = stability_api.generate(prompt, **request)
    artifacts = process_artifacts_from_answers(
        filename, prompt, answers, write=True, verbose=False
    )

    showimages = False

    if showimages:
        for artifact in open_images(artifacts, verbose=True):
            pass
    else:
        for artifact in artifacts:
            pass


def generate_images(prompts, quality=25):
    counter = 1
    for prompt in tqdm(prompts, desc="Generating images"):
        generate_image(prompt, f"./tmp/{counter}-", quality)
        counter += 1