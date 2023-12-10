"""
Implements logic gate nodes
"""
import re
from .autonode import node_wrapper, get_node_names_mappings, validate


classes = []
node = node_wrapper(classes)

@node
class LogicGateCompareFloat:
    """
    Returns 1 if input1 > input2, 0 otherwise
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
    FUNCTION = "compareFloat"
    CATEGORY = "Logic Gates"
    custom_name = "ABiggerThanB(Float)"
    def compareFloat(self, input1, input2):
        return (1.0 if input1 > input2 else 0.0,)
@node
class LogicGateInvertBasic:
    """
    Inverts 1 to 0 and 0 to 1
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "invert"
    CATEGORY = "Logic Gates"
    custom_name = "Invert Basic"
    def invert(self, input1):
        return (1 if input1 == 0 else 0,)
@node
class LogicGateInvertValueInt:
    """
    Inverts x -> -x
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "invertValue"
    CATEGORY = "Logic Gates"
    custom_name = "Invert Value Int"
    def invertValue(self, input1):
        return (-input1,)
@node
class LogicGateInvertValueFloat:
    """
    Inverts x -> -x
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT", {"default": 0.0}),
        }
    }
    FUNCTION = "invertValue"
    CATEGORY = "Logic Gates"
    custom_name = "Invert Value Float"
    def invertValue(self, input1):
        return (-input1,)
@node
class LogicGateBitwiseShift:
    """
    Shifts input1 by input2 bits
    Only works on integers
    Negative input2 shifts right, positive input2 shifts left
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
    FUNCTION = "bitwiseShift"
    CATEGORY = "Logic Gates"
    custom_name = "Bitwise Shift"
    def bitwiseShift(self, input1, input2):
        # validate input2
        if abs(input2) > 32:
            raise ValueError("input2 must be between -32 and 32")
        return (input1 << input2,)
@node
class LogicGateBitwiseAnd:
    """
    Bitwise AND of input1 and input2
    Only works on integers
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
    FUNCTION = "bitwiseAnd"
    CATEGORY = "Logic Gates"
    custom_name = "Bitwise And"
    def bitwiseAnd(self, input1, input2):
        return (input1 & input2,)
@node
class LogicGateBitwiseOr:
    """
    Bitwise OR of input1 and input2
    Only works on integers
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
    FUNCTION = "bitwiseOr"
    CATEGORY = "Logic Gates"
    custom_name = "Bitwise Or"
    def bitwiseOr(self, input1, input2):
        return (input1 | input2,)
@node
class LogicGateBitwiseXor:
    """
    Bitwise XOR of input1 and input2
    Only works on integers
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
    FUNCTION = "bitwiseXor"
    CATEGORY = "Logic Gates"
    custom_name = "Bitwise Xor"
    def bitwiseXor(self, input1, input2):
        return (input1 ^ input2,)
@node
class LogicGateBitwiseNot:
    """
    Bitwise NOT of input1
    Only works on integers
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT", {"default": 0}),
        }
    }
    FUNCTION = "bitwiseNot"
    CATEGORY = "Logic Gates"
    custom_name = "Bitwise Not"
    def bitwiseNot(self, input1):
        return (~input1,)
@node
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
    custom_name = "ABiggerThanB(Int)"
    def compareInt(self, input1, input2):
        return (1 if input1 > input2 else 0,)
@node
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
    custom_name = "AContainsB(String)"
    def compareString(self, regex, input2):
        return (1 if re.search(regex, input2) else 0,)
@node
class LogicGateEitherFloat:
    """
    Returns input1 if condition is true, input2 otherwise
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "condition": ("INT", {"default": 0}),
            "input1": ("FLOAT", {"default": 0}),
            "input2": ("FLOAT", {"default": 0}),
        }
    }
    FUNCTION = "either"
    CATEGORY = "Logic Gates"
    custom_name = "ConditionAorB(Float)"
    def either(self, condition, input1, input2):
        return (input1 if condition else input2,)
@node
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
    custom_name = "ConditionAorB(Int)"
    def either(self, condition, input1, input2):
        return (input1 if condition else input2,)
@node
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
    custom_name = "Static Number Int"
    def staticNumber(self, number):
        return (number,)
@node
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
    custom_name = "Static Number Float"
    def staticNumber(self, number):
        return (number,)
@node
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
    custom_name = "Static String"
    def staticString(self, string):
        return (string,)
@node
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
    custom_name = "And Int"
    def and_(self, input1, input2):
        return (1 if input1 and input2 else 0,)
@node
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
    custom_name = "And Float"
    def and_(self, input1, input2):
        return (1 if input1 and input2 else 0,)
@node
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
    custom_name = "Or Int"
    def or_(self, input1, input2):
        return (1 if input1 and input2 else 0,)
@node
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
    custom_name = "Or Float"
    def or_(self, input1, input2):
        return (1 if input1 and input2 else 0,)
@node
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
    custom_name = "Either String"
    def either(self, condition, input1, input2):
        return (input1 if condition else input2,)
@node
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
    custom_name = "Add Int"
    def add(self, input1, input2):
        return (input1 + input2,)
@node
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
    custom_name = "Add Float"
    def add(self, input1, input2):
        return (input1 + input2,)
@node
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
    custom_name = "Merge String"
    def merge(self, input1, input2):
        return (input1 + input2,)

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(classes)
validate(classes)
