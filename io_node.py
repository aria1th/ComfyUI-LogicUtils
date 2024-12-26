import base64
import json
import numpy as np
import torch
try:
    import piexif.helper
    import piexif
    from .exif.exif import read_info_from_image_stealth
    piexif_loaded = True
except ImportError:
    piexif_loaded = False

from .imgio.converter import PILHandlingHodes
from .autonode import node_wrapper, get_node_names_mappings, validate, anytype, PILImage
import time
import os
from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance
from PIL.PngImagePlugin import PngInfo
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

def throw_if_parent_or_root_access(path):
    if ".." in path or path.startswith("/") or path.startswith("\\"):
        raise RuntimeError("Invalid path")
    if path.startswith("~"):
        raise RuntimeError("Invalid path")
    if os.path.isabs(path):
        raise RuntimeError("Path cannot be absolute")

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
    RESULT_NODE = True
    CATEGORY = "image"
    custom_name = "Save Image Custom Node" 

    def save_images(self, images, filename_prefix="ComfyUI",subfolder_dir="", prompt=None, extra_pnginfo=None):
        if images is None: # sometimes images is empty
            images = []
        filename_prefix += self.prefix_append
        throw_if_parent_or_root_access(filename_prefix)
        throw_if_parent_or_root_access(subfolder_dir)
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
    RESULT_NODE = True
    OUTPUT_NODE = True
    
    def save_text(self, text, filename_prefix="ComfyUI",subfolder_dir="",filename=""):
        text = str(text)
        throw_if_parent_or_root_access(filename_prefix)
        throw_if_parent_or_root_access(subfolder_dir)
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
                 "optional": {"quality": ("INT", {"default": 100}), "lossless": ("BOOLEAN", {"default": False}), "compression": ("INT", {"default": 4}), "optimize": ("BOOLEAN", {"default": False}), "metadata_string": ("STRING", {"default": ""})},
                "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
                }

    RETURN_TYPES = ("STRING",) #Filename
    FUNCTION = "save_images"

    OUTPUT_NODE = True
    RESULT_NODE = True

    CATEGORY = "image"
    custom_name = "Save Image Webp Node" 

    def save_images(self, images, filename_prefix="ComfyUI",subfolder_dir="", prompt=None, extra_pnginfo=None, quality=100, lossless=False, compression=4, optimize=False, metadata_string=""):
        if images is None: # sometimes images is empty
            images = []
        throw_if_parent_or_root_access(filename_prefix)
        throw_if_parent_or_root_access(subfolder_dir)
        filename_prefix += self.prefix_append
        output_dir = os.path.join(self.output_dir, subfolder_dir)
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for image in images:
            i = 255. * image.cpu().numpy()
            clipped = np.clip(i, 0, 255).astype(np.uint8)
            if clipped.shape[0] <= 3:
                clipped = np.transpose(clipped, (1, 2, 0)) #[1216, 832, 3]
            img = Image.fromarray(clipped)
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
            if piexif_loaded:
                exif_bytes = piexif.dump({
                    "Exif": {
                        piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(json.dumps(metadata) or "", encoding="unicode")
                    },
                })
            file = f"{filename}_{counter:05}_.webp"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=compression, quality=quality, lossless=lossless, optimize=optimize)
            if piexif_loaded:
                piexif.insert(exif_bytes, os.path.join(full_output_folder, file))
            
            results.append({
                "filename": os.path.join(full_output_folder, file),
                "subfolder": subfolder_dir,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results }, "outputs": { "images": os.path.join(full_output_folder, file).rstrip('.webp') } }

@fundamental_node
class ComposeRGBAImageFromMask:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "mask": ("MASK",),
                "invert": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "compose"
    CATEGORY = "image"
    custom_name = "Compose RGBA Image From Mask"
    @staticmethod
    def compose(image, mask, invert):
        if invert:
            mask = 1.0 - mask

        # Ensure mask has shape (batch_size, height, width, 1)
        mask = mask.reshape((-1, mask.shape[-2], mask.shape[-1], 1))
        # check devices, move to cpu
        if hasattr(image, "device"):
            image = image.cpu()
        if hasattr(mask, "device"):
            mask = mask.cpu()
        # Resize mask to match image dimensions if necessary
        if image.shape[0] != mask.shape[0] or image.shape[1] != mask.shape[1] or image.shape[2] != mask.shape[2]:
            # Resize mask to match image dimensions
            mask = torch.nn.functional.interpolate(
                mask.permute(0, 3, 1, 2),
                size=(image.shape[1], image.shape[2]),
                mode="bilinear",
                align_corners=False
            ).permute(0, 2, 3, 1)

        num_channels = image.shape[-1]
        if num_channels == 3:
            rgba_image = torch.cat((image, mask), dim=-1)
        elif num_channels == 4:
            rgba_image = image.clone()
            rgba_image[:, :, :, 3:] = mask
        else:
            raise ValueError("Image must have 3 (RGB) or 4 (RGBA) channels")

        return (rgba_image,)

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
class ResizeImageEnsuringMultiple:
    FUNCTION = "resize_image_ensuring_multiple"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Image Ensuring W/H Multiple"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_image_ensuring_multiple(image, multiple, method):
        image = PILHandlingHodes.handle_input(image)
        image_width, image_height = image.size
        total_pixels = image_width * image_height
        if total_pixels == 0:
            raise RuntimeError("Image has no pixels")
        target_width = (image_width // multiple) * multiple
        target_height = (image_height // multiple) * multiple
        return (image.resize((target_width, target_height), ResizeImageResolution.constants[method]),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "multiple": ("INT", {"default": 32}),
                "method": (["NEAREST", "LANCZOS", "BICUBIC"],),
            },
        }
@fundamental_node
class ResizeImageResolutionIfBigger:
    FUNCTION = "resize_image_resolution_if_bigger"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Image With Resolution If Bigger"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_image_resolution_if_bigger(image, resolution, method):
        image = PILHandlingHodes.handle_input(image)
        image_width, image_height = image.size
        total_pixels = image_width * image_height
        if total_pixels == 0:
            raise RuntimeError("Image has no pixels")
        if total_pixels <= resolution ** 2:
            return (image,)
        # get ratio
        target_pixels = resolution ** 2
        ratio = target_pixels / total_pixels
        target_width = int(image_width * ratio)
        target_height = int(image_height * ratio)
        return (image.resize((target_width, target_height), ResizeImageResolutionIfBigger.constants[method]),)
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
class ResizeImageResolutionIfSmaller:
    FUNCTION = "resize_image_resolution_if_smaller"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Resize Image With Resolution If Smaller"
    
    constants = {
        "NEAREST": Image.Resampling.NEAREST,
        "LANCZOS": Image.Resampling.LANCZOS,
        "BICUBIC": Image.Resampling.BICUBIC,
    }
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def resize_image_resolution_if_smaller(image, resolution, method):
        image = PILHandlingHodes.handle_input(image)
        image_width, image_height = image.size
        total_pixels = image_width * image_height
        if total_pixels == 0:
            raise RuntimeError("Image has no pixels")
        if total_pixels >= resolution ** 2:
            return (image,)
        # get ratio
        target_pixels = resolution ** 2
        ratio = target_pixels / total_pixels
        target_width = int(image_width * ratio)
        target_height = int(image_height * ratio)
        return (image.resize((target_width, target_height), ResizeImageResolutionIfSmaller.constants[method]),)
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
class Base64DecodeNode:
    FUNCTION = "base64_decode"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Base64 Decode to Image"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def base64_decode(base64_string):
        image = PILHandlingHodes.handle_input(base64_string) # automatically converts to PIL image
        return (image,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_string": ("STRING",),
            }
        }

@fundamental_node
class ImageFromURLNode:
    FUNCTION = "url_download"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Download Image from URL"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def url_download(url):
        if not url.startswith("http"): # for security reasons
            raise RuntimeError("Invalid URL")
        image = PILHandlingHodes.handle_input(url) # automatically downloads image
        return (image,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING",),
            }
        }

@fundamental_node
class Base64EncodeNode:
    FUNCTION = "base64_encode"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "image"
    custom_name = "Image to Base64 Encode"
    @staticmethod
    def base64_encode(image, quality, format, gzip_compress):
        image = PILHandlingHodes.to_base64(image, quality, format, gzip_compress)
        return (image,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "quality": ("INT", {"default": 100}),
                "format": (["PNG", "WEBP", "JPG"], {"default": "PNG"}),
                "gzip_compress": ("BOOLEAN", {"default": False}),
            }
        }

@fundamental_node
class StringToBase64Node:
    FUNCTION = "string_to_base64"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "image"
    custom_name = "String to Base64 Encode"
    @staticmethod
    def string_to_base64(string, gzip_compress):
        return (PILHandlingHodes.string_to_base64(string, gzip_compress),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "string": ("STRING",),
            },
            "optional": {
                "gzip_compress": ("BOOLEAN", {"default": False}),
            }
        }

@fundamental_node
class Base64ToStringNode:
    FUNCTION = "base64_to_string"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "image"
    custom_name = "Base64 to String Decode"
    @staticmethod
    def base64_to_string(base64_string):
        return (PILHandlingHodes.maybe_gzip_base64_to_string(base64_string),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base64_string": ("STRING",),
            }
        }

@fundamental_node
class InvertImageNode:
    FUNCTION = "invert_image"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Invert Image"
    @staticmethod
    @PILHandlingHodes.output_wrapper
    def invert_image(image):
        image = PILHandlingHodes.handle_input(image)
        return (ImageOps.invert(image),)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            }
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
                "size": ("INT", {"default": 2}),
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
class GetImageInfoNode:
    FUNCTION="get_image_info"
    RETURN_TYPES=("WIDTH", "HEIGHT", "TOTAL_PIXELS")
    CATEGORY="image"
    custom_name="Get Image Info"
    @staticmethod
    def get_image_info(image):
        image = PILHandlingHodes.handle_input(image)
        width, height = image.size
        return (width, height, width * height)
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
