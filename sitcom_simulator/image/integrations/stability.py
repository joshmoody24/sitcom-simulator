import tempfile
import mimetypes
import os
import logging

STABILITY_HOST = "grpc.stability.ai:443"

def generate_image(prompt:str, width:int=1024, height:int=1024):
    """
    Generates an image for each prompt using stable diffusion,
    returning a list of file paths for those images

    :param prompt: The prompt to generate the image for
    :param width: The width of the image to generate
    :param height: The height of the image to generate
    """
    # lazy load because this is a heavy dependency
    import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
    from stability_sdk.client import StabilityInference, process_artifacts_from_answers

    # customize engine here if desired (default is newest)
    # i.e. engine='stable-diffusion-v1-5'
    stability_api = StabilityInference(
        STABILITY_HOST,
        key=os.getenv('STABILITY_API_KEY'),
        verbose=False,
        )
        
    answers = stability_api.generate(
        prompt=prompt,
        width=width,
        height=height,
        )
        
    artifacts = process_artifacts_from_answers(
        prefix="", prompt=prompt, answers=answers, write=False, verbose=False
    )
    
    img_path = None
    
    for file_path, artifact in artifacts:
        if artifact.type == generation.ARTIFACT_IMAGE:
            ext = mimetypes.guess_extension(artifact.mime)
            contents = artifact.binary
            logging.debug("writing", file_path, "to temporary file")
            with tempfile.NamedTemporaryFile(suffix=ext, delete=False, mode='wb') as tmp_img:
                tmp_img.write(contents)
                img_path = tmp_img.name
            break
    if not img_path:
        raise Exception("Image not found in artifacts")
    logging.debug("Generated image:", img_path)
    return img_path