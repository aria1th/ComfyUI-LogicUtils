from .imgio.converter import PILHandlingHodes
from .autonode import node_wrapper, get_node_names_mappings, validate, anytype, PILImage
from .utils.tagger import get_tags, tagger_keys

auxilary_classes = []
auxilary_node = node_wrapper(auxilary_classes)

@auxilary_node
class GetRatingNode:
    FUNCTION = "get_rating_class"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "tagger"
    custom_name = "Get Rating Class"
    @staticmethod
    def get_rating_class(image, model_name):
        image = PILHandlingHodes.handle_input(image)
        result_dict = get_tags(image, model_name=model_name)
        return (result_dict['rating'], )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }

@auxilary_node
class GetRatingFromTextNode:
    FUNCTION = "get_rating_class"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "tagger"
    custom_name = "Get Rating Class From Text"
    @staticmethod
    def get_rating_class(image, model_name):
        image = PILHandlingHodes.handle_input(image)
        result_dict = get_tags(image, model_name=model_name)
        return (result_dict['rating'], )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("STRING", {"default": "/path/to/image.jpg"}),
            },
            "optional": {
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }

@auxilary_node
class GetTagsAboveThresholdNode:
    FUNCTION = "get_tags_above_threshold"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "tagger"
    custom_name = "Get Tags Above Threshold"
    @staticmethod
    def get_tags_above_threshold(image, threshold, replace, model_name):
        image = PILHandlingHodes.handle_input(image)
        result_dict = get_tags(image, threshold=threshold, replace=replace, model_name=model_name)
        return (", ".join(result_dict['tags']), )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "threshold": ("FLOAT", {"default": 0.4}),
                "replace": ("BOOLEAN", {"default": False}),
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }

@auxilary_node
class GetTagsAboveThresholdFromTextNode:
    FUNCTION = "get_tags_above_threshold"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "tagger"
    custom_name = "Get Tags Above Threshold From Text"
    @staticmethod
    def get_tags_above_threshold(image, threshold, replace, model_name):
        image = PILHandlingHodes.handle_input(image)
        result_dict = get_tags(image, threshold=threshold, replace=replace, model_name=model_name)
        return (", ".join(result_dict['tags']), )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "threshold": ("FLOAT", {"default": 0.4}),
                "replace": ("BOOLEAN", {"default": False}),
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }
        
@auxilary_node
class GetCharactersAboveThresholdNode:
    FUNCTION = "get_tags_above_threshold"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "tagger"
    custom_name = "Get Chars Above Threshold"
    @staticmethod
    def get_tags_above_threshold(image, threshold, replace, model_name):
        image = PILHandlingHodes.handle_input(image)
        result_dict = get_tags(image, threshold=threshold, replace=replace, model_name=model_name)
        return (", ".join(result_dict['chars']), )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "threshold": ("FLOAT", {"default": 0.4}),
                "replace": ("BOOLEAN", {"default": False}),
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }

@auxilary_node
class GetCharactersAboveThresholdFromTextNode:
    FUNCTION = "get_tags_above_threshold"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "tagger"
    custom_name = "Get Chars Above Threshold From Text"
    @staticmethod
    def get_tags_above_threshold(image, threshold, replace, model_name):
        image = PILHandlingHodes.handle_input(image)
        result_dict = get_tags(image, threshold=threshold, replace=replace, model_name=model_name)
        return (", ".join(result_dict['chars']), )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "threshold": ("FLOAT", {"default": 0.4}),
                "replace": ("BOOLEAN", {"default": False}),
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }

@auxilary_node
class GetAllTagsAboveThresholdNode:
    FUNCTION = "get_tags"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "tagger"
    custom_name = "Get All Tags Above Threshold"
    @staticmethod
    def get_tags(image, threshold, replace, model_name):
        image = PILHandlingHodes.handle_input(image)
        result = get_tags(image, threshold=threshold, replace=replace, model_name=model_name)
        result_list = []
        result_list.append(result['rating'])
        result_list.extend(result['tags'])
        result_list.extend(result['chars'])
        return (", ".join(result_list), )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
            },
            "optional": {
                "threshold": ("FLOAT", {"default": 0.4}),
                "replace": ("BOOLEAN", {"default": False}),
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(auxilary_classes)
validate(auxilary_classes)