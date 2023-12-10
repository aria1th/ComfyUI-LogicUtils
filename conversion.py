"""
Converts int / float / boolean
Note that it depends on the order of the conversion
"""
from .autonode import validate, node_wrapper, get_node_names_mappings
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
        FUNCTION = class_name.lower()
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

for type_from in conversion_operators:
    for type_to in conversion_operators:
        create_class(type_from, type_to)

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(classes)
validate(classes)
