"""
AutoNode setup - AngelBottomless@github
# By following the example, you can prepare "decorator" that will automatically collect required information for node registration.
fundamental_classes = []
fundamental_node = node_wrapper(fundamental_classes)

# Then, you can define the classes that will be used in the node. "FUNCTION", "INPUT_TYPES", "RETURN_TYPES", "CATEGORY" attributes are used for node registration.
# You can set "custom_name" attribute to set the name of the node that will be displayed in the UI.
# Pleare run validate(fundamental_classes) to check if all required attributes are set.
# You can also use anytype to represent any type of input.
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

# Then, at the end of each node registeration class, run the following to set up static variables.
CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(fundamental_classes)

# Then, at the other script - here, nodes.py, you can import the CLASS_MAPPINGS and CLASS_NAMES to register the nodes.
from .io_node import CLASS_MAPPINGS as IOMapping, CLASS_NAMES as IONames

# it collects NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS, and updates them with the new mappings. Note that same keys will be overwritten.

# Finally, at the __init__.py, you can import the NODE_CLASS_MAPPINGS and NODE_DISPLAY_NAME_MAPPINGS to register the nodes.
from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

# Then, you can use the registered nodes in the UI!
"""
from inspect import signature

def get_node_names_mappings(classes):
    node_names = {}
    node_classes = {}
    for cls in classes:
        # check if "custom_name" attribute is set
        if hasattr(cls, "custom_name"):
            node_names[cls.__name__] = cls.custom_name
            node_classes[cls.__name__] = cls
    return node_classes, node_names

def node_wrapper(container):
    def wrap_class(cls):
        container.append(cls)
        return cls
    return wrap_class

def validate(container):
    # check if "custom_name", "FUNCTION", "INPUT_TYPES", "RETURN_TYPES", "CATEGORY" attributes are set
    for cls in container:
        for attr in ["FUNCTION", "INPUT_TYPES", "RETURN_TYPES", "CATEGORY"]:
            if not hasattr(cls, attr):
                raise Exception("Class {} doesn't have attribute {}".format(cls.__name__, attr))
        return_type = cls.RETURN_TYPES
        if not isinstance(return_type, tuple):
            raise Exception(f"RETURN_TYPES must be a tuple, got {type(return_type)} in {cls.__name__}")
        if not all(isinstance(x, str) for x in return_type):
            raise Exception(f"RETURN_TYPES must be a tuple of strings, got {return_type} in {cls.__name__}")
        input_keys = ["self"]
        for key in cls.INPUT_TYPES()["required"]:
            input_keys.append(key)
        for key in cls.INPUT_TYPES().get("optional", {}):
            input_keys.append(key)
        function_kwargs = signature(cls.__dict__[cls.FUNCTION]).parameters.keys()
        function_kwargs = list(function_kwargs) + ["self"]
        # if args/kwargs are in function kwargs, warn and skip
        if "args" in function_kwargs:
            #print(f"Warning: args in function arguments in {cls.__name__}, skipping argument validation")
            continue
        if "kwargs" in function_kwargs:
            #print(f"Warning: kwargs in function arguments in {cls.__name__}, skipping argument validation")
            continue
        # input kwargs are subset of function kwargs
        if not set(input_keys).issubset(function_kwargs):
            raise Exception(f"INPUT_TYPES and function arguments must match in {cls.__name__}, input_types: {input_keys}, function arguments: {function_kwargs}")
        # if not exact match, print warning
        if len(set(input_keys)) != len(set(function_kwargs)):
            #print(f"Warning: INPUT_TYPES and function arguments don't match in {cls.__name__}, input_types: {input_keys}, function arguments: {function_kwargs}")
            pass
# AllTrue class hijacks the isinstance, issubclass, bool, str, jsonserializable, eq, ne methods to always return True
class AllTrue(str):
    def __init__(self, representation=None) -> None:
        self.repr = representation
        pass
    def __ne__(self, __value: object) -> bool:
        return False
    # isinstance, jsonserializable hijack
    def __instancecheck__(self, instance):
        return True
    def __subclasscheck__(self, subclass):
        return True
    def __bool__(self):
        return True
    def __str__(self):
        return self.repr
    # jsonserializable hijack
    def __jsonencode__(self):
        return self.repr
    def __repr__(self) -> str:
        return self.repr
    def __eq__(self, __value: object) -> bool:
        return True
anytype = AllTrue("*") # when a != b is called, it will always return False
PILImage = object() # dummy object to represent PIL.Image