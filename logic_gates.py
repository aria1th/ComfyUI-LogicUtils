"""
Implements logic gate nodes
"""
import re
class LogicGateCompareFloat:
    """
    Returns 1 if input1 > input2, 0 otherwise
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT", {"default": 0.0}),
            "input2": ("FLOAT", {"default": 0.0}),
        }
    }
    FUNCTION = "compareFloat"
    CATEGORY = "Logic Gates"
    def compareFloat(self, input1, input2):
        return 1.0 if input1 > input2 else 0.0
    
class LogicGateCompareInt:
    """
    Returns 1 if input1 > input2, 0 otherwise
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT", {"default": 0}),
            "input2": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "compareInt"
    CATEGORY = "Logic Gates"
    def compareInt(self, input1, input2):
        return 1 if input1 > input2 else 0

class LogicGateCompareString:
    """
    Returns if given regex (1) is found in given string (2)
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "regex": ("STRING", {"default": ""}),
            "input2": ("STRING", {"default": ""}),
        }
    }
    FUNCTION = "compareString"
    CATEGORY = "Logic Gates"
    def compareString(self, regex, input2):
        return 1 if re.search(regex, input2) else 0

class LogicGateEitherFloat:
    """
    Returns input1 if condition is true, input2 otherwise
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "condition": ("INT", {"default": 0}),
            "input1": ("INT", {"default": 0}),
            "input2": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "either"
    CATEGORY = "Logic Gates"
    def either(self, condition, input1, input2):
        return input1 if condition else input2

class LogicGateEitherInt:
    """
    Returns input1 if condition is true, input2 otherwise
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "condition": ("INT", {"default": 0}),
            "input1": ("INT", {"default": 0}),
            "input2": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "either"
    CATEGORY = "Logic Gates"
    def either(self, condition, input1, input2):
        return input1 if condition else input2

class StaticNumberInt:
    """
    Returns a static number
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "number": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "staticNumber"
    CATEGORY = "Logic Gates"
    def staticNumber(self, number):
        return number

class StaticNumberFloat:
    """
    Returns a static number
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "number": ("FLOAT", {"default": 0.0}),
        }
    }
    FUNCTION = "staticNumber"
    CATEGORY = "Logic Gates"
    def staticNumber(self, number):
        return number

class StaticString:
    """
    Returns a static string
    """
    RETURN_TYPES = ("STRING",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "string": ("STRING", {"default": ""}),
        }
    }
    FUNCTION = "staticString"
    CATEGORY = "Logic Gates"
    def staticString(self, string):
        return string

class LogicGateAndInt:
    """
    Returns 1 if all inputs are True, 0 otherwise
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT", {"default": 0}),
            "input2": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "and_"
    CATEGORY = "Logic Gates"
    def and_(self, input1, input2):
        return 1 if input1 and input2 else 0

class LogicGateAndFloat:
    """
    Returns 1 if all inputs are True, 0 otherwise
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT", {"default": 0.0}),
            "input2": ("FLOAT", {"default": 0.0}),
        }
    }
    FUNCTION = "and_"
    CATEGORY = "Logic Gates"
    def and_(self, input1, input2):
        return 1 if input1 and input2 else 0
class LogicGateOrInt:
    """
    Returns 1 if any input is True, 0 otherwise
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT", {"default": 0}),
            "input2": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "or_"
    CATEGORY = "Logic Gates"
    def or_(self, input1, input2):
        return 1 if input1 or input2 else 0
class LogicGateOrFloat:
    """
    Returns 1 if any input is True, 0 otherwise
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT", {"default": 0.0}),
            "input2": ("FLOAT", {"default": 0.0}),
        }
    }
    FUNCTION = "or_"
    CATEGORY = "Logic Gates"
    def or_(self, input1, input2):
        return 1 if input1 or input2 else 0    

class LogicGateEitherString:
    """
    Returns input1 if condition is true, input2 otherwise
    """
    RETURN_TYPES = ("STRING",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "condition": ("INT", {"default": 0}),
            "input1": ("STRING", {"default": ""}),
            "input2": ("STRING", {"default": ""}),
        }
    }
    FUNCTION = "either"
    CATEGORY = "Logic Gates"
    def either(self, condition, input1, input2):
        return input1 if condition else input2

class AddInt:
    """
    Returns the sum of the inputs
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT", {"default": 0}),
            "input2": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "add"
    CATEGORY = "Logic Gates"
    def add(self, input1, input2):
        return input1 + input2

class AddFloat:
    """
    Returns the sum of the inputs
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT", {"default": 0.0}),
            "input2": ("FLOAT", {"default": 0.0}),
        }
    }
    FUNCTION = "add"
    CATEGORY = "Logic Gates"
    def add(self, input1, input2):
        return input1 + input2

class MergeString:
    """
    Returns the concatenation of the inputs
    """
    RETURN_TYPES = ("STRING",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("STRING", {"default": ""}),
            "input2": ("STRING", {"default": ""}),
        }
    }
    FUNCTION = "merge"
    CATEGORY = "Logic Gates"
    def merge(self, input1, input2):
        return input1 + input2

CLASS_MAPPINGS = {
    "LogicGateCompareFloat": LogicGateCompareFloat,
    "LogicGateCompareInt": LogicGateCompareInt,
    "LogicGateCompareString": LogicGateCompareString,
    "LogicGateEitherFloat": LogicGateEitherFloat,
    "LogicGateEitherInt": LogicGateEitherInt,
    "StaticNumberInt": StaticNumberInt,
    "StaticNumberFloat": StaticNumberFloat,
    "StaticString": StaticString,
    "LogicGateAndInt": LogicGateAndInt,
    "LogicGateAndFloat": LogicGateAndFloat,
    "LogicGateOrInt": LogicGateOrInt,
    "LogicGateOrFloat": LogicGateOrFloat,
    "LogicGateEitherString": LogicGateEitherString,
    "AddInt": AddInt,
    "AddFloat": AddFloat,
    "MergeString": MergeString,
}

CLASS_NAMES = {
    "LogicGateCompareFloat": "ABiggerThanB(Float)",
    "LogicGateCompareInt": "ABiggerThanB(Int)",
    "LogicGateCompareString": "AContainsB(String)",
    "LogicGateEitherFloat": "ConditionAorB(Float)",
    "LogicGateEitherInt": "ConditionAorB(Int)",
    "StaticNumberInt": "Static Number Int",
    "StaticNumberFloat": "Static Number Float",
    "StaticString": "Static String",
    "LogicGateAndInt": "And(Int)",
    "LogicGateAndFloat": "And(Float)",
    "LogicGateOrInt": "Or(Int)",
    "LogicGateOrFloat": "Or(Float)",
    "LogicGateEitherString": "Either String",
    "AddInt": "Add Int",
    "AddFloat": "Add Float",
    "MergeString": "Merge String",
}
