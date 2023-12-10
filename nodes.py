
from .logic_gates import CLASS_MAPPINGS as LogicMapping, CLASS_NAMES as LogicNames
from .randomness import CLASS_MAPPINGS as RandomMapping, CLASS_NAMES as RandomNames
from .conversion import CLASS_MAPPINGS as ConversionMapping, CLASS_NAMES as ConversionNames
from .autonode import node_wrapper, get_node_names_mappings, validate
import time

fundamental_classes = []
fundamental_node = node_wrapper(fundamental_classes)

@fundamental_node
class SleepNodeFloat:
    FUNCTION = "sleep"
    RETURN_TYPES = ("FLOAT",)
    CATEGORY = "Misc"
    custom_name = "Sleep (Float tunnel)"
    @staticmethod
    def sleep(interval):
        time.sleep(interval)
        return (interval,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "interval": ("FLOAT", {"default": 0.0}),
            }
        }
@fundamental_node
class SleepNodeImage:
    FUNCTION = "sleep"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "Misc"
    custom_name = "Sleep (Image tunnel)"
    @staticmethod
    def sleep(interval, image):
        time.sleep(interval)
        return (None,)
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "interval": ("FLOAT", {"default": 0.0}),
                "image": ("IMAGE",),
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

# https://github.com/comfyanonymous/ComfyUI/blob/340177e6e85d076ab9e222e4f3c6a22f1fb4031f/custom_nodes/example_node.py.example#L18
@fundamental_node
class TextPreviewNode:
    """
    Displays text in the UI
    """
    FUNCTION = "text_preview"
    RETURN_TYPES = ()
    CATEGORY = "Misc"
    OUTPUT_NODE = True
    custom_name = "Text Preview"
    def __init__(self) -> None:
        self.type = "output"

    def text_preview(self, text):
        print(text)
        # below does not work, why?
        return {"ui": {"text": text}}
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING",{"default": "text"}),
            }
        }

classes_parsed, node_names_parsed = get_node_names_mappings(fundamental_classes)
validate(fundamental_classes)

NODE_CLASS_MAPPINGS = {
}
NODE_CLASS_MAPPINGS.update(classes_parsed)
NODE_CLASS_MAPPINGS.update(LogicMapping)
NODE_CLASS_MAPPINGS.update(RandomMapping)
NODE_CLASS_MAPPINGS.update(ConversionMapping)
NODE_DISPLAY_NAME_MAPPINGS = {

}
NODE_DISPLAY_NAME_MAPPINGS.update(node_names_parsed)
NODE_DISPLAY_NAME_MAPPINGS.update(LogicNames)
NODE_DISPLAY_NAME_MAPPINGS.update(RandomNames)
NODE_DISPLAY_NAME_MAPPINGS.update(ConversionNames)
