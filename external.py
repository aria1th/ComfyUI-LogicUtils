from .autonode import node_wrapper, get_node_names_mappings, validate, anytype
from .imgio.converter import PILHandlingHodes
from .webuiapi.out_api import get_image_from_prompt, get_image_from_prompt_fallback

from PIL import Image


external_classes = []
external_nodes = node_wrapper(external_classes)


@external_nodes

class SDWebuiAPINode:
    FUNCTION = "get_image_from_prompt"
    RETURN_TYPES = ("IMAGE",)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": ""}),
                "api_endpoint": ("STRING", {"default": ""}),
            },
            "optional": {
                "auth": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": -1}),
                "negative_prompt": ("STRING", {"default": ""}),
                "steps": ("INT", {"default": 28}),
                "width": ("INT", {"default": 1024}),
                "height": ("INT", {"default": 1024}),
                "hr_scale": ("FLOAT", {"default": 1.5}),
                "hr_upscale": ("STRING", {"default": "Latent"}),
                "enable_hr": ("BOOL", {"default": False}),
                "cfg_scale": ("INT", {"default": 7}),
            }
        }
    CATEGORY = "WebUI API"
    custom_name = "Get Image From Prompt"
    @PILHandlingHodes.output_wrapper
    def get_image_from_prompt(self, prompt, api_endpoint, auth="", seed=-1, negative_prompt="", steps=28, width=1024, height=1024, hr_scale=1.5, hr_upscale="Latent", enable_hr=False, cfg_scale=7):
        return (get_image_from_prompt(prompt, api_endpoint, auth, seed, negative_prompt, steps, width, height, hr_scale, hr_upscale, enable_hr, cfg_scale)[0],)
@external_nodes
class SDWebuiAPIFallbackNode:
    FUNCTION = "get_image_from_prompt_fallback"
    RETURN_TYPES = ("IMAGE",)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": ""}),
                "api_endpoint": ("STRING", {"default": ""}),
            },
            "optional": {
                "auth": ("STRING", {"default": ""}),
                "seed": ("INT", {"default": -1}),
                "negative_prompt": ("STRING", {"default": ""}),
                "steps": ("INT", {"default": 28}),
                "width": ("INT", {"default": 1024}),
                "height": ("INT", {"default": 1024}),
                "hr_scale": ("FLOAT", {"default": 1.5}),
                "hr_upscale": ("STRING", {"default": "Latent"}),
                "enable_hr": ("BOOL", {"default": False}),
                "cfg_scale": ("INT", {"default": 7}),
            }
        }
    CATEGORY = "WebUI API"
    custom_name = "Get Image From Prompt (Fallback)"
    @PILHandlingHodes.output_wrapper
    def get_image_from_prompt_fallback(self, prompt, api_endpoint, auth="", seed=-1, negative_prompt="", steps=28, width=1024, height=1024, hr_scale=1.5, hr_upscale="Latent", enable_hr=False, cfg_scale=7):
        return (get_image_from_prompt_fallback(prompt, api_endpoint, auth, seed, negative_prompt, steps, width, height, hr_scale, hr_upscale, enable_hr, cfg_scale)[0],)

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(external_classes)
validate(external_classes)