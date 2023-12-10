"""
Converts int / float / boolean
Note that it depends on the order of the conversion
"""
from .autonode import validate, node_wrapper, get_node_names_mappings, anytype
classes = []
node = node_wrapper(classes)

conversion_operators = {
    "Int" : int,
    "Float" : float,
    "Bool" : bool,
    "String" : str
}
def create_class(type_from, type_to):
    if type_from == type_to:
        return None
    class_name = "{}2{}".format(type_from, type_to)
    class CustomClass:
        FUNCTION = "convert"
        RETURN_TYPES = (type_to.upper(),)
        CATEGORY = "Conversion"
        custom_name = "Convert {} to {}".format(type_from, type_to)
        @staticmethod
        def convert(input1):
            return (conversion_operators[type_to](input1),)
        @classmethod
        def INPUT_TYPES(cls):
            return {
            "required": {
                "input1": (type_from.upper(), {"default": 0.0}),
            }
        }
    CustomClass.__name__ = class_name
    node(CustomClass)
    return CustomClass


@node
class StringListToCombo:
    """
    Converts raw string, separates with separator, then return as raw list
    """
    RETURN_TYPES = (anytype,)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "string": ("STRING", {"default": ""}),
            "separator": ("STRING", {"default": "$"}),
        }
    }
    FUNCTION = "stringListToCombo"
    CATEGORY = "Logic Gates"
    custom_name = "String List to Combo"
    def stringListToCombo(self, string, separator):
        return (string.split(separator),)

@node
class ConvertComboToString:
    """
    Converts raw list to string, separated with separator
    """
    RETURN_TYPES = ("STRING",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "combo": (anytype, {"default": []}),
            "separator": ("STRING", {"default": "$"}),
        }
    }
    FUNCTION = "convertComboToString"
    CATEGORY = "Logic Gates"
    custom_name = "Convert Combo to String"
    def convertComboToString(self, combo, separator):
        if isinstance(combo, (str, float, int, bool)):
            return (combo,)
        return (separator.join(combo),)

for type_from in conversion_operators:
    for type_to in conversion_operators:
        create_class(type_from, type_to)

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(classes)
validate(classes)
