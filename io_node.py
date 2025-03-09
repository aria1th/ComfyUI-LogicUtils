import base64
import json
import math
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
import shutil
from PIL import Image
from PIL import ImageOps
from PIL import ImageEnhance
from PIL.PngImagePlugin import PngInfo
import folder_paths
from comfy.cli_args import args
import filelock
import tempfile

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
class CurrentTimestamp:
    """
    Returns the current Unix timestamp or a formatted time string.
    """
    def __init__(self):
        pass

    def generate(self, format_string):
        if format_string.strip() == "":
            # return Unix timestamp
            return (int(time.time()),)
        else:
            # return formatted date/time
            return (time.strftime(format_string, time.localtime()),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "format_string": ("STRING", {
                    "default": "",
                    "display": "text",
                    "comment": "Leave blank for raw timestamp, or use format directives like '%Y-%m-%d %H:%M:%S'"
                }),
            }
        }

    RETURN_TYPES = ("STRING",)  # or ("INT",) if returning raw int timestamp
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Current Timestamp"

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
    Can't display text but it makes always changed state
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
    @classmethod
    def IS_CHANGED(s, *args, **kwargs):
        return float("nan")

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
        raise RuntimeError("Tried to access parent or root directory")
    if path.startswith("~"):
        raise RuntimeError("Tried to access home directory")
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

        return { "ui": { "texts": results }, "outputs": { "images": file.rstrip('.txt') } }

@fundamental_node
class DumpTextJsonlNode:
    """
    Appends text to a JSONL file (one JSON object per line).
    Each line will have the structure: { "<keyname>": "<text_item>" }

    For concurrency safety, this node uses filelock to block
    concurrent writes to the same file.
    """
    FUNCTION = "dump_text_jsonl"
    RETURN_TYPES = ("STRING",)  # We return the filename for convenience
    CATEGORY = "text"
    custom_name = "Dump Text JSONL Node"
    RESULT_NODE = True
    OUTPUT_NODE = True

    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"  # for consistent UI listing
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(cls):
        """
        text can be a single string or a list of strings. 
        If it's a list, each item is appended as a separate line.
        """
        return {
            "required": {
                "text": (anytype, ),  # Single string or list of strings
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "subfolder_dir": ("STRING", {"default": ""}),
                "filename": ("STRING", {"default": "dump.jsonl"}),
                "keyname": ("STRING", {"default": "text"}),
            },
        }

    def dump_text_jsonl(
        self,
        text,
        filename_prefix="ComfyUI",
        subfolder_dir="",
        filename="dump.jsonl",
        keyname="text",
    ):
        # Security checks to avoid writing outside of the ComfyUI output folder
        throw_if_parent_or_root_access(filename_prefix)
        throw_if_parent_or_root_access(subfolder_dir)

        # Build the actual output path
        filename_prefix += self.prefix_append  # If you want to append something
        output_dir = os.path.join(self.output_dir, subfolder_dir)
        os.makedirs(output_dir, exist_ok=True)

        final_filename = filename_prefix + "_" + filename
        full_path = os.path.join(output_dir, final_filename)
        lock_path = full_path + ".lock"

        # Ensure we can safely write concurrently
        with filelock.FileLock(lock_path, timeout=10):
            with open(full_path, "a", encoding="utf-8") as f:
                # If `text` is a list, write each element as its own JSON line
                if isinstance(text, list):
                    for item in text:
                        # Convert each item to string, just to be safe
                        line = {keyname: str(item)}
                        f.write(json.dumps(line, ensure_ascii=False) + "\n")
                else:
                    # Single string input
                    line = {keyname: str(text)}
                    f.write(json.dumps(line, ensure_ascii=False) + "\n")

        # Return data for UI usage
        results = [
            {
                "filename": final_filename,
                "subfolder": subfolder_dir,
                "type": self.type
            }
        ]
        return {
            "ui": {"texts": results},
            "outputs": {"filename": final_filename},
        }


@fundamental_node
class ConcatGridNode:
    """
    Concatenate multiple images in a row, a column, or a square-like grid
    using either resizing or padding to match dimensions.

    direction:
        - "horizontal": line up side by side
        - "vertical": stack top to bottom
        - "square-like": arrange images in an NxN grid (where N = ceil(sqrt(#images)))

    match_method:
        - "resize": scale images so their matching dimension is the same
                    (height for horizontal, width for vertical, or cell-size for square-like)
        - "pad": keep original size but add transparent padding so the matching dimension is the same
    """

    FUNCTION = "concat_grid"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Concat Grid (Batch to single grid)"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "direction": (
                    ["horizontal", "vertical", "square-like"],
                    {"default": "horizontal"},
                ),
                "match_method": (["resize", "pad"], {"default": "resize"}),
            }
        }

    @staticmethod
    @PILHandlingHodes.output_wrapper
    def concat_grid(images, direction="horizontal", match_method="resize"):
        # 1) Convert images input to a list of PIL RGBA images
        #    - If it's a torch.Tensor with shape (B, C, H, W) or a single image, unify into list.
        if not (
            isinstance(images, torch.Tensor) and len(images.shape) == 4
        ) and not isinstance(images, (list, tuple)):
            images = [images]

        converted = PILHandlingHodes.handle_input(images)  # returns PIL or list of PIL
        if isinstance(converted, list):
            pil_images = [img.convert("RGBA") for img in converted]
        else:
            pil_images = [converted.convert("RGBA")]

        if len(pil_images) == 0:
            raise RuntimeError("No images provided to Concat Grid")

        # 2) Handle the three layout directions
        if direction == "horizontal":
            # --- Horizontal layout ---
            max_height = max(img.height for img in pil_images)
            processed = []
            for img in pil_images:
                if match_method == "resize":
                    # Scale the image so that height == max_height
                    if img.height == 0:
                        raise RuntimeError("Encountered an image of zero height.")
                    ratio = max_height / float(img.height)
                    new_w = int(img.width * ratio)
                    new_h = max_height
                    new_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                else:  # "pad"
                    # Create a new image with the same width but max_height
                    new_img = Image.new("RGBA", (img.width, max_height), (0, 0, 0, 0))
                    new_img.paste(img, (0, 0))
                processed.append(new_img)

            total_width = sum(im.width for im in processed)
            out = Image.new("RGBA", (total_width, max_height), (0, 0, 0, 0))
            x_offset = 0
            for im in processed:
                out.paste(im, (x_offset, 0))
                x_offset += im.width

        elif direction == "vertical":
            # --- Vertical layout ---
            max_width = max(img.width for img in pil_images)
            processed = []
            for img in pil_images:
                if match_method == "resize":
                    if img.width == 0:
                        raise RuntimeError("Encountered an image of zero width.")
                    ratio = max_width / float(img.width)
                    new_w = max_width
                    new_h = int(img.height * ratio)
                    new_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
                else:  # "pad"
                    new_img = Image.new("RGBA", (max_width, img.height), (0, 0, 0, 0))
                    new_img.paste(img, (0, 0))
                processed.append(new_img)

            total_height = sum(im.height for im in processed)
            out = Image.new("RGBA", (max_width, total_height), (0, 0, 0, 0))
            y_offset = 0
            for im in processed:
                out.paste(im, (0, y_offset))
                y_offset += im.height

        else:  # direction == "square-like"
            # --- Square-like NxN grid ---
            count = len(pil_images)
            # Determine grid size
            num_cols = int(math.ceil(math.sqrt(count)))
            num_rows = int(math.ceil(count / num_cols))

            # Find maximum width/height among images
            max_width = max(img.width for img in pil_images)
            max_height = max(img.height for img in pil_images)

            processed = []
            for img in pil_images:
                if match_method == "resize":
                    # Here we forcibly resize each image to (max_width, max_height)
                    # (which may distort if aspect ratios differ).
                    new_img = img.resize(
                        (max_width, max_height), Image.Resampling.LANCZOS
                    )
                else:  # "pad"
                    # Keep original size but create a new RGBA canvas so each cell is (max_w, max_h)
                    new_img = Image.new("RGBA", (max_width, max_height), (0, 0, 0, 0))
                    new_img.paste(img, (0, 0))
                processed.append(new_img)

            # Create the final output canvas
            grid_width = num_cols * max_width
            grid_height = num_rows * max_height
            out = Image.new("RGBA", (grid_width, grid_height), (0, 0, 0, 0))

            # Paste images in row-major order
            idx = 0
            for row in range(num_rows):
                for col in range(num_cols):
                    if idx >= count:
                        break  # no more images
                    x_offset = col * max_width
                    y_offset = row * max_height
                    out.paste(processed[idx], (x_offset, y_offset))
                    idx += 1

        return (out,)


@fundamental_node
class ConcatTwoImagesNode:
    """
    Concatenate exactly two images (imageA, imageB).

    direction:
        - "horizontal": line them up side by side
        - "vertical": place them top to bottom

    match_method:
        - "resize": scale images so their matching dimension is the same
          (height for horizontal, width for vertical)
        - "pad": keep original size but pad them so the matching dimension is the same
    """

    FUNCTION = "concat_two_images"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Concat 2 Images to Grid"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "imageA": ("IMAGE",),
                "imageB": ("IMAGE",),
                "direction": (["horizontal", "vertical"], {"default": "horizontal"}),
                "match_method": (["resize", "pad"], {"default": "resize"}),
            }
        }

    @staticmethod
    @PILHandlingHodes.output_wrapper
    def concat_two_images(
        imageA, imageB, direction="horizontal", match_method="resize"
    ):
        # Convert input to PIL images (RGBA to preserve alpha if needed)
        pilA = PILHandlingHodes.handle_input(imageA)
        if isinstance(pilA, list):
            raise RuntimeError("Expected a single image for imageA, grid only supports two images")
        pilB = PILHandlingHodes.handle_input(imageB)
        if isinstance(pilB, list):
            raise RuntimeError("Expected a single image for imageB, grid only supports two images")
        if direction == "horizontal":
            # We want to unify heights
            max_h = max(pilA.height, pilB.height)

            if match_method == "resize":
                # Scale each image so their heights match
                def scale_height(img, target_h):
                    if img.height == 0:
                        raise RuntimeError("Encountered an image with zero height.")
                    ratio = target_h / float(img.height)
                    new_w = int(img.width * ratio)
                    new_h = target_h
                    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                pilA = scale_height(pilA, max_h)
                pilB = scale_height(pilB, max_h)

            else:  # match_method == "pad"
                # Pad images with transparent background so they share the same height
                def pad_height(img, target_h):
                    new_img = Image.new("RGBA", (img.width, target_h), (0, 0, 0, 0))
                    new_img.paste(img, (0, 0))
                    return new_img

                pilA = pad_height(pilA, max_h)
                pilB = pad_height(pilB, max_h)

            total_width = pilA.width + pilB.width
            out = Image.new("RGBA", (total_width, max_h), (0, 0, 0, 0))
            # Paste images side by side
            out.paste(pilA, (0, 0))
            out.paste(pilB, (pilA.width, 0))

        else:
            # direction == "vertical"
            # We want to unify widths
            max_w = max(pilA.width, pilB.width)

            if match_method == "resize":
                # Scale each image so their widths match
                def scale_width(img, target_w):
                    if img.width == 0:
                        raise RuntimeError("Encountered an image with zero width.")
                    ratio = target_w / float(img.width)
                    new_w = target_w
                    new_h = int(img.height * ratio)
                    return img.resize((new_w, new_h), Image.Resampling.LANCZOS)

                pilA = scale_width(pilA, max_w)
                pilB = scale_width(pilB, max_w)

            else:  # match_method == "pad"
                # Pad images with transparent background so they share the same width
                def pad_width(img, target_w):
                    new_img = Image.new("RGBA", (target_w, img.height), (0, 0, 0, 0))
                    new_img.paste(img, (0, 0))
                    return new_img

                pilA = pad_width(pilA, max_w)
                pilB = pad_width(pilB, max_w)

            total_height = pilA.height + pilB.height
            out = Image.new("RGBA", (max_w, total_height), (0, 0, 0, 0))
            # Paste images top to bottom
            out.paste(pilA, (0, 0))
            out.paste(pilB, (0, pilA.height))

        return (out,)

@fundamental_node
class SaveCustomJPGNode:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE",),
                "filename_prefix": ("STRING", {"default": "ComfyUI"}),
                "subfolder_dir": ("STRING", {"default": ""}),
            },
            "optional": {
                "quality": ("INT", {"default": 95}),
                "optimize": ("BOOLEAN", {"default": True}),
                "metadata_string": ("STRING", {"default": ""})
            },
            "hidden": {"prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"},
        }

    RETURN_TYPES = ("STRING",)  # Filename
    FUNCTION = "save_images"

    OUTPUT_NODE = True
    RESULT_NODE = True

    CATEGORY = "image"
    custom_name = "Save Custom JPG Node"

    def save_images(self, images, filename_prefix="ComfyUI", subfolder_dir="", prompt=None, extra_pnginfo=None,
                    quality=95, optimize=True, metadata_string=""):
        if images is None:
            images = []
        if not isinstance(images, (list, tuple, torch.Tensor)):
            images = [images]

        throw_if_parent_or_root_access(filename_prefix)
        throw_if_parent_or_root_access(subfolder_dir)

        filename_prefix += self.prefix_append
        output_dir = os.path.join(self.output_dir, subfolder_dir)
        filelock_path = os.path.join(output_dir, filename_prefix + ".lock")

        results = []
        for image in images:
            if isinstance(image, torch.Tensor):
                if image.device.type != "cpu":
                    image = image.cpu()
                image = 255. * image.numpy()
                clipped = np.clip(image, 0, 255).astype(np.uint8)
                if clipped.shape[0] <= 3:
                    clipped = np.transpose(clipped, (1, 2, 0))
                img = Image.fromarray(clipped)
            else:
                img = PILHandlingHodes.handle_input(image)

            metadata = {}
            if not args.disable_metadata:
                if prompt is not None:
                    metadata["prompt"] = json.dumps(prompt)
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata[x] = json.dumps(extra_pnginfo[x])

            if metadata_string:
                metadata = {"metadata": metadata_string}

            exif_bytes = None
            if piexif_loaded:
                exif_bytes = piexif.dump({
                    "Exif": {
                        piexif.ExifIFD.UserComment: piexif.helper.UserComment.dump(json.dumps(metadata), encoding="unicode")
                    },
                })

            with filelock.FileLock(filelock_path, timeout=10):
                full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(
                    filename_prefix, output_dir, img.size[1], img.size[0])
                counter_len = len(str(len(images)))
                file = f"{filename}_{str(counter).zfill(max(5, counter_len))}_.jpg"

                with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmpfile:
                    tmp_path = tmpfile.name
                    img.save(tmp_path, "JPEG", quality=quality, optimize=optimize)

                if piexif_loaded and exif_bytes:
                    piexif.insert(exif_bytes, tmp_path)

                final_path = os.path.join(full_output_folder, file)
                shutil.copy2(tmp_path, final_path)
                os.remove(tmp_path)

            results.append({
                "filename": os.path.join(full_output_folder, file),
                "subfolder": subfolder_dir,
                "type": self.type
            })

        return {"ui": {"images": results}, "outputs": {"images": os.path.join(full_output_folder, file).rstrip('.jpg')}}

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
        if not isinstance(images, (list, tuple, torch.Tensor)):
            images = [images]
        throw_if_parent_or_root_access(filename_prefix)
        throw_if_parent_or_root_access(subfolder_dir)
        filename_prefix += self.prefix_append
        output_dir = os.path.join(self.output_dir, subfolder_dir)
        filelock_path = os.path.join(output_dir, filename_prefix + ".lock")
        
        results = list()
        for image in images:
            if isinstance(image, torch.Tensor):
                if image.device.type != "cpu":
                    image = image.cpu()
                image = 255. * image.numpy()
                clipped = np.clip(image, 0, 255).astype(np.uint8)
                if clipped.shape[0] <= 3:
                    clipped = np.transpose(clipped, (1, 2, 0)) #[1216, 832, 3]
                img = Image.fromarray(clipped)
            else:
                img = PILHandlingHodes.handle_input(image)
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
            
            with filelock.FileLock(filelock_path, timeout=10): # timeout 10 seconds should be enough for most cases
                full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, output_dir, img.size[1], img.size[0])
                counter_len = len(str(len(images))) # for padding
                #file = f"{filename}_{counter:05}_.webp"
                file = f"{filename}_{str(counter).zfill(max(5, counter_len))}_.webp"
                with tempfile.NamedTemporaryFile(suffix=".webp", delete=False) as tmpfile:
                    tmp_path = tmpfile.name
                    img.save(tmp_path, "WEBP", pnginfo=metadata, compress_level=compression, quality=quality, lossless=lossless, optimize=optimize)
                if piexif_loaded:
                    piexif.insert(exif_bytes, tmp_path)
                final_path = os.path.join(full_output_folder, file)
                shutil.copy2(tmp_path, final_path)
                os.remove(tmp_path)
            
            results.append({
                "filename": os.path.join(full_output_folder, file),
                "subfolder": subfolder_dir,
                "type": self.type
            })

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
                "width": ("INT", {"default": 512}),
                "height": ("INT", {"default": 512}),
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
        ratio = (target_pixels / total_pixels) ** 0.5
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
            raise RuntimeError("Strict URL check is required, however the URL does not start with http")
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
                "scale": ("INT", {"default": 2}),
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
