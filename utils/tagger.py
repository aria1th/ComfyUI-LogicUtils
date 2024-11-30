try:
    from imgutils.tagging import get_wd14_tags
except ImportError:
    def get_wd14_tags(image_path):
        raise Exception("Tagger feature not available, please install dghs-imgutils")
from typing import Union
from PIL import Image

def get_rating_class(rating):
    # argmax
    return max(rating, key=rating.get)

def get_tags_above_threshold(tags, threshold=0.4):
    return [tag for tag, score in tags.items() if score > threshold]

def replace_underscore(tag):
    return tag.replace('_', ' ')

def get_tags(image_path:Union[str, Image.Image], threshold:float = 0.4, replace:bool = False) -> dict[str, list[str]]:
    result = {}
    rating, features, chars = get_wd14_tags(image_path)
    result['rating'] = get_rating_class(rating)
    result['tags'] = get_tags_above_threshold(features, threshold)
    result['chars'] = get_tags_above_threshold(chars, threshold)
    if replace:
        result['tags'] = [replace_underscore(tag) for tag in result['tags']]
        result['chars'] = [replace_underscore(tag) for tag in result['chars']]
    return result
