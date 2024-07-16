

import json
import numpy as np
import piexif.helper

from .exif.exif import read_info_from_image_stealth
from .imgio.converter import IOConverter, PILHandlingHodes
from .autonode import node_wrapper, get_node_names_mappings, validate, anytype, PILImage
import time
import os
from PIL import Image
from PIL import ImageEnhance
from PIL.PngImagePlugin import PngInfo
import piexif
import folder_paths
from comfy.cli_args import args

fundamental_classes = []
fundamental_node = node_wrapper(fundamental_classes)

@fundamental_node
class SleepNodeAny:
    FUNCTION = "sleep"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Misc"
    custom_name = "SleepNode"
    @staticmethod
    def sleep(interval, inputs):
        time.sleep(interval)
        return (inputs,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "interval": ("FLOAT", {"default": 0.0}),
            },
            "optional": {
                "inputs": (anytype, {"default": 0.0}),
            }
        }
@fundamental_node
class SleepNodeImage:
    FUNCTION = "sleep"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Misc"
    custom_name = "Sleep (Image tunnel)"
    @staticmethod
    def sleep(interval, image):
        time.sleep(interval)
        return (image,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "interval": ("FLOAT", {"default": 0.0}),
                "image": (anytype,),
            }
        }

@fundamental_node
class ErrorNode:
    FUNCTION = "raise_error"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "Misc"
    custom_name = "ErrorNode"
    @staticmethod
    def raise_error(error_msg = "Error"):
        raise Exception("Error: {}".format(error_msg))
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "error_msg": ("STRING", {"default": "Error"}),
            }
        }

@fundamental_node
class DebugComboInputNode:
    FUNCTION = "debug_combo_input"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "Misc"
    custom_name = "Debug Combo Input"
    @staticmethod
    def debug_combo_input(input1):
        print(input1)
        return (input1,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input1": (["0", "1", "2"], { "default": "0" }),
            }
        }

# https://github.com/comfyanonymous/ComfyUI/blob/340177e6e85d076ab9e222e4f3c6a22f1fb4031f/custom_nodes/example_node.py.example#L18
@fundamental_node
class TextPreviewNode:
    """
    Displays text in the UI
    """
    FUNCTION = "text_preview"
    RETURN_TYPES = ()
    CATEGORY = "Misc"
    custom_name = "Text Preview"
    RESULT_NODE = True
    OUTPUT_NODE = True

    def text_preview(self, text):
        print(text)
        # below does not work, why?
        return {"ui": {"text": str(text)}}
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": (anytype,{"default": "text", "type" : "output"}),
            }
        }

@fundamental_node
class ParseExifNode:
    """
    Parses exif data from image
    """
    FUNCTION = "parse_exif"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "Misc"
    custom_name = "Parse Exif"
    @staticmethod
    def parse_exif(image):
        return (read_info_from_image_stealth(image),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }


@fundamental_node
class SaveImageCustomNode:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required": 
                    {"images": ("IMAGE", ),
                     "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                     "subfolder_dir": ("STRING", {"default": ""}),
                     },
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = ("STRING",) #Filename
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "image"
    custom_name = "Save Image Custom Node" 

    def save_images(self, images, filename_prefix="ComfyUI",subfolder_dir="", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        output_dir = os.path.join(self.output_dir, subfolder_dir)
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            file = f"{filename}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results }, "outputs": { "images": file.rstrip('.png') } }

@fundamental_node
class SaveTextCustomNode:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {"required": 
                    {"text": (anytype, ),
                     "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                     "subfolder_dir": ("STRING", {"default": ""}),
                     "filename": ("STRING", {"default": ""}),
                     },
                }
    
    RETURN_TYPES = ("STRING",) #Filename
    FUNCTION = "save_text"
    custom_name = "Save Text Custom Node"
    CATEGORY = "text"

    def save_text(self, text, filename_prefix="ComfyUI",subfolder_dir="",filename=""):
        text = str(text)
        assert len(text) > 0 and len(filename) > 0, "Text and filename must be non-empty"
        filename_prefix += self.prefix_append
        output_dir = os.path.join(self.output_dir, subfolder_dir)
        filename_merged = filename_prefix + filename + ".txt"
        full_output_folder, subfolder, actual_filename = output_dir, "", filename_merged 
        results = list()
        file = actual_filename
        with open(os.path.join(full_output_folder, file), "w") as f:
            f.write(text)
        results.append({
            "filename": file,
            "subfolder": subfolder,
            "type": self.type
        })
        counter += 1

        return { "ui": { "texts": results }, "outputs": { "images": file.rstrip('.txt') } }

@fundamental_node
class SaveImageWebpCustomNode:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {"required": 
                    {"images": ("IMAGE", ),
                     "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                     "subfolder_dir": ("STRING", {"default": ""}),
                     },
                 "optional": {"quality": ("INT", {"default": 100}), "lossless": ("BOOL", {"default": False}), "compression": ("INT", {"default": 4}), "optimize": ("BOOL", {"default": False}), "metadata_string": ("STRING", {"default": ""})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = ("STRING",) #Filename
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "image"
    custom_name = "Save Image Webp Node" 

    def save_images(self, images, filename_prefix="ComfyUI",subfolder_dir="", prompt=None, extra_pnginfo=None, quality=100, lossless=False, compression=4, optimize=False, metadata_string=""):
        filename_prefix += self.prefix_append
        output_dir = os.path.join(self.output_dir, subfolder_dir)
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = {}
                if prompt is not None:
                    metadata["prompt"] = json.dumps(prompt)
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata[x] = json.dumps(extra_pnginfo[x])
            if metadata_string:# override metadata
                metadata = {}
                metadata["metadata"]= metadata_string
            exif_bytes = piexif.dump({
                "Exif": {
                    piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(json.dumps(metadata) or "", encoding="unicode")
                },
            })
            file = f"{filename}_{counter:05}_.webp"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=compression, quality=quality, lossless=lossless, optimize=optimize)
            
            piexif.insert(exif_bytes, os.path.join(full_output_folder, file))
            
            results.append({
                "filename": os.path.join(full_output_folder, file),
                "subfolder": subfolder_dir,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results }, "outputs": { "images": os.path.join(full_output_folder, file).rstrip('.webp') } }

@fundamental_node
class ResizeImageNode:
    FUNCTION = "resize_image"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Image"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_image(image, width, height, method):
        image = PILHandlingHodes.handle_input(image)
        return (image.resize((width, height), ResizeImageNode.constants[method]),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {"default": 512}),
                "method": (["NEAREST", "LANCZOS", "BICUBIC"],),
            },
        }

@fundamental_node
class ResizeImageResolution:
    FUNCTION = "resize_image_resolution"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Image With Resolution"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_image_resolution(image, resolution, method):
        image = PILHandlingHodes.handle_input(image)
        image_width, image_height = image.size
        total_pixels = image_width * image_height
        if total_pixels == 0:
            raise RuntimeError("Image has no pixels")
        if resolution < 256:
            raise RuntimeError("Resolution must be positive and at least 256")
        # get ratio
        target_pixels = resolution ** 2
        ratio = target_pixels / total_pixels
        target_width = int(image_width * ratio)
        target_height = int(image_height * ratio)
        return (image.resize((target_width, target_height), ResizeImageResolution.constants[method]),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "resolution": ("INT", {"default": 512}),
                "method": (["NEAREST", "LANCZOS", "BICUBIC"],),
            },
        }

@fundamental_node
class ResizeScaleImageNode:
    FUNCTION = "resize_scale_image"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Scale Image"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_scale_image(image, scale, method):
        image = PILHandlingHodes.handle_input(image)
        if scale < 0:
            raise RuntimeError("Scale must be positive")
        return (image.resize((int(image.width*scale), int(image.height*scale)), ResizeScaleImageNode.constants[method]),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {"default": 512}),
                "method": (["NEAREST", "LANCZOS", "BICUBIC"],),
            },
        }

@fundamental_node
class ResizeShortestToNode:
    FUNCTION = "resize_shortest_to"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Shortest To"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_shortest_to(image, size, method):
        image = PILHandlingHodes.handle_input(image)
        if size < 0:
            raise RuntimeError("Size must be positive")
        if image.width < image.height:
            return (image.resize((size, int(image.height* size/image.width)), ResizeShortestToNode.constants[method]),)
        else:
            return (image.resize((int(image.width* size/image.height), size), ResizeShortestToNode.constants[method]),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {"default": 512}),
                "method": (["NEAREST", "LANCZOS", "BICUBIC"],),
            },
        }

@fundamental_node
class ResizeLongestToNode:
    FUNCTION = "resize_longest_to"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Longest To"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_longest_to(image, size, method):
        image = PILHandlingHodes.handle_input(image)
        if size < 0:
            raise RuntimeError("Size must be positive")
        if image.width > image.height:
            return (image.resize((size, int(image.height* size/image.width)), ResizeLongestToNode.constants[method]),)
        else:
            return (image.resize((int(image.width* size/image.height), size), ResizeLongestToNode.constants[method]),)
        
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "size": ("INT", {"default": 512}),
                "method": (["NEAREST", "LANCZOS", "BICUBIC"],),
            },
        }


@fundamental_node
class ConvertGreyscaleNode:
    FUNCTION = "convert_greyscale"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Convert Greyscale"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def convert_greyscale(image):
        image = PILHandlingHodes.handle_input(image)
        greyscale_image = image.convert("L")
        # 3 channel greyscale image
        return (greyscale_image.convert("RGB"),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }
        
@fundamental_node
class RotateImageNode:
    FUNCTION = "rotate_image"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Rotate Image"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def rotate_image(image, angle):
        image = PILHandlingHodes.handle_input(image)
        return (image.rotate(angle),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "angle": ("INT", {"default": 0}),
            }
        }

@fundamental_node
class BrightnessNode:
    FUNCTION = "brightness"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Brightness"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def brightness(image, factor):
        image = PILHandlingHodes.handle_input(image)
        enhancer = ImageEnhance.Brightness(image)
        return (enhancer.enhance(factor),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "factor": ("FLOAT", {"default": 1.0}),
            }
        }

@fundamental_node
class ContrastNode:
    FUNCTION = "contrast"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Contrast"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def contrast(image, factor):
        image = PILHandlingHodes.handle_input(image)
        enhancer = ImageEnhance.Contrast(image)
        return (enhancer.enhance(factor),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "factor": ("FLOAT", {"default": 1.0}),
            }
        }

@fundamental_node
class SharpnessNode:
    FUNCTION = "sharpness"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Sharpness"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def sharpness(image, factor):
        image = PILHandlingHodes.handle_input(image)
        enhancer = ImageEnhance.Sharpness(image)
        return (enhancer.enhance(factor),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "factor": ("FLOAT", {"default": 1.0}),
            }
        }

@fundamental_node
class ColorNode:
    FUNCTION = "color"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Color"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def color(image, factor):
        image = PILHandlingHodes.handle_input(image)
        enhancer = ImageEnhance.Color(image)
        return (enhancer.enhance(factor),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "factor": ("FLOAT", {"default": 1.0}),
            }
        }

@fundamental_node
class ConvertRGBNode:
    FUNCTION = "convert_rgb"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Convert RGB"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def convert_rgb(image):
        image = PILHandlingHodes.handle_input(image)
        return (image.convert("RGB"),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
        }

@fundamental_node
class ThresholdNode:
    FUNCTION = "threshold"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Threshold image with value"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def threshold(image, threshold):
        image = PILHandlingHodes.handle_input(image)
        return (image.point(lambda p: p > threshold and 255),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "threshold": ("INT", {"default": 128}),
            }
        }

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(fundamental_classes)
validate(fundamental_classes)
