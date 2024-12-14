from .imgio.converter import PILHandlingHodes
from .autonode import node_wrapper, get_node_names_mappings, validate, anytype, PILImage
from .utils.tagger import get_tags, tagger_keys
from PIL import Image

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
class CensorImageByRating:
    FUNCTION = "censor_image"
    RETURN_TYPES = ("IMAGE",)
    CATEGORY = "image"
    custom_name = "Censor Image by Rating"

    @staticmethod
    @PILHandlingHodes.output_wrapper
    def censor_image(image, rating_threshold, censor_method, model_name=None):
        # Convert input to a PIL image
        image = PILHandlingHodes.handle_input(image)
        result_dict = get_tags(image, model_name=model_name)
        rating = result_dict['rating']
        # If rating is general, no censorship required
        if rating.lower() == "general":
            return (image,)
        censor_image = False
        if rating_threshold == "general":
            # censor if not general
            if rating.lower() != "general":
                censor_image = True
        elif rating_threshold == "sensitive":
            # censor if not general or sensitive
            if rating.lower() not in ["general", "sensitive"]:
                censor_image = True
        elif rating_threshold == "questionable":
            # censor if not general, sensitive or questionable
            if rating.lower() not in ["general", "sensitive", "questionable"]:
                censor_image = True
        elif rating_threshold == "explicit":
            return (image,) # why are you using this?
        if censor_image:
            if censor_method.lower() == "white":
                # Return a white image of the same size
                censored_image = Image.new("RGB", image.size, (255, 255, 255))
                return (censored_image,)

            elif censor_method.lower() == "blur":
                from PIL import ImageFilter
                # Apply a strong blur (you can adjust radius as needed)
                censored_image = image.filter(ImageFilter.GaussianBlur(radius=20))
                return (censored_image,)

        # If unknown method is provided, just return the original image
        return (image,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "rating_threshold": (["general", "sensitive", "questionable", "explicit"],),
                "censor_method": (["blur", "white"],),
            },
            "optional": {
                "model_name": (tagger_keys, {"default": tagger_keys[0]}),
            }
        }

@auxilary_node
class FilterTagsNode:
    """
    Filters tags, given a list of tags splitted by ",".
    We assume the input text is splittable by "," (or separator). Then, if any tags contain the filter, we remove matching tags.
    """
    FUNCTION = "filter_tags"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "safety"
    custom_name = "Filter Tags"
    @staticmethod
    def filter_tags(tags, filter_tags, separator):
        filter_tags = filter_tags.split(",")
        filter_tags = [tag.strip() for tag in filter_tags]
        tags = tags.split(separator)
        tags = [tag.strip() for tag in tags]
        filtered = []
        for tag in tags:
            if all(filter_tag not in tag for filter_tag in filter_tags):
                filtered.append(tag)
        return (separator.join(filtered), )
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "tags": ("STRING",),
                "filter_tags": ("STRING",),
            },
            # optional separator
            "optional": {
                "separator": ("STRING", {"default": ","}),
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
