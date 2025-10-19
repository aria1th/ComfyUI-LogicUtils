try:
    from imgutils.tagging import get_wd14_tags
    from imgutils.tagging.wd14 import MODEL_NAMES as tagger_model_names
except ImportError:
    def get_wd14_tags(image_path):
        raise Exception("Tagger feature not available, please install dghs-imgutils")
    tagger_model_names = {
        "EVA02_Large": None,
        "ViT_Large": None,
        "SwinV2": None,
        "ConvNext": None,
        "ConvNextV2": None,
        "ViT": None,
        "MOAT": None,
        "SwinV2_v3": None,
        "ConvNext_v3": None,
        "ViT_v3": None,
    }
from typing import Union
from PIL import Image

def get_rating_class(rating):
    # argmax
    return max(rating, key=rating.get)

def get_tags_above_threshold(tags, threshold=0.4):
    return [tag for tag, score in tags.items() if score > threshold]

def replace_underscore(tag):
    return tag.replace('_', ' ')

def get_tags(image_path:Union[str, Image.Image], threshold:float = 0.4, replace:bool = False, model_name:str = "SwinV2") -> dict[str, list[str]]:
    result = {}
    rating, features, chars = get_wd14_tags(image_path, model_name)
    result['rating'] = get_rating_class(rating)
    result['tags'] = get_tags_above_threshold(features, threshold)
    result['chars'] = get_tags_above_threshold(chars, threshold)
    if replace:
        result['tags'] = [replace_underscore(tag) for tag in result['tags']]
        result['chars'] = [replace_underscore(tag) for tag in result['chars']]
    return result
try:
    tagger_keys = list(tagger_model_names.keys())
except NameError:
    tagger_keys = []
