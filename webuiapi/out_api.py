import requests
import json
from PIL import Image
import io
import base64
from typing import Optional


def send_request(api_endpoint:str, auth:Optional[str], arguments:dict) -> list[Image.Image]:
    session = requests.Session()
    if auth:
        session.auth = (auth.split(":")[0], auth.split(":")[1])
    api_endpoint = api_endpoint.rstrip("/") + "/sdapi/v1/txt2img"
    response = session.post(api_endpoint, json=arguments)
    response.raise_for_status()
    response_json = response.json()
    if "images" in response_json.keys():
        images = [Image.open(io.BytesIO(base64.b64decode(i))) for i in response_json["images"]]
    elif "image" in response_json.keys():
        images = [Image.open(io.BytesIO(base64.b64decode(response_json["image"])))]
    else:
        raise ValueError("No image data in response")
    return images

def construct_args(
    prompt:str,
    seed:int=-1,
    negative_prompt:Optional[str] = None,
    steps:int = 28,
    width:int = 1024,
    height:int = 1024,
    hr_scale:float = 1.5,
    hr_upscale:str = "Latent",
    enable_hr:bool = False,
    cfg_scale:int = 7,
):
    arguments = {
        "prompt": prompt,
        "seed": seed,
        "steps": steps,
        "width": width,
        "height": height,
        "hr_scale": hr_scale,
        "hr_upscale": hr_upscale,
        "enable_hr": enable_hr,
        "cfg_scale": cfg_scale,
    }
    if negative_prompt:
        arguments["negative_prompt"] = negative_prompt
    else:
        arguments["negative_prompt"] = ""
    return arguments

def get_image_from_prompt(
    prompt:str,
    api_endpoint:str,
    auth:Optional[str]=None,
    seed:int=-1,
    negative_prompt:Optional[str] = None,
    steps:int = 28,
    width:int = 1024,
    height:int = 1024,
    hr_scale:float = 1.5,
    hr_upscale:str = "Latent",
    enable_hr:bool = False,
    cfg_scale:int = 7,
):
    arguments = construct_args(
        prompt=prompt,
        seed=seed,
        negative_prompt=negative_prompt,
        steps=steps,
        width=width,
        height=height,
        hr_scale=hr_scale,
        hr_upscale=hr_upscale,
        enable_hr=enable_hr,
        cfg_scale=cfg_scale,
    )
    return send_request(api_endpoint, auth, arguments)

def get_image_from_prompt_fallback(
    prompt:str,
    api_endpoint:str,
    auth:Optional[str]=None,
    seed:int=-1,
    negative_prompt:Optional[str] = None,
    steps:int = 28,
    width:int = 1024,
    height:int = 1024,
    hr_scale:float = 1.5,
    hr_upscale:str = "Latent",
    enable_hr:bool = False,
    cfg_scale:int = 7,
):
    arguments = construct_args(
        prompt=prompt,
        seed=seed,
        negative_prompt=negative_prompt,
        steps=steps,
        width=width,
        height=height,
        hr_scale=hr_scale,
        hr_upscale=hr_upscale,
        enable_hr=enable_hr,
        cfg_scale=cfg_scale,
    )
    try:
        return send_request(api_endpoint, auth, arguments)
    except Exception as e:
        # create blank image
        return [Image.new("RGB", (width, height), (255, 255, 255))]
