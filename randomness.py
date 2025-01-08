import random
import uuid
from .autonode import node_wrapper, get_node_names_mappings, validate


classes = []
node = node_wrapper(classes)

class RandomGuaranteedClass:
    @classmethod
    def IS_CHANGED(s, *args, **kwargs):
       return random.SystemRandom().random()
    
@node
class SystemRandomFloat(RandomGuaranteedClass):
    """
    Random number generator using system randomness
    """
    def __init__(self):
        pass
    @staticmethod
    def generate(min_val=0.0, max_val=1.0, precision=0):
        instance = random.SystemRandom()
        value = instance.uniform(min_val, max_val)
        if precision > 0:
            value = round(value, precision)
        return (value,)
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "min_val": ("FLOAT", { "default": 0.0, "min": -999999999, "max": 999999999.0, "step": 0.01, "display": "number" }),
                "max_val": ("FLOAT", { "default": 1.0, "min": -999999999, "max": 999999999.0, "step": 0.01, "display": "number" }),
                "precision": ("INT", { "default": 0, "min": 0, "max": 10, "step": 1, "display": "number" }),
            },
        }
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "System Random Float"
    @classmethod
    def IS_CHANGED(s, min_val, max_val, precision):
       return random.SystemRandom().random()

@node
class SystemRandomInt(RandomGuaranteedClass):
    """
    Random number generator using system randomness
    Generates an integer value between 0 and 2^32-1
    """

    def __init__(self):
        pass
    @staticmethod
    def generate(min_val=0, max_val=2**32 - 1):
        instance = random.SystemRandom()
        value = instance.randint(min_val, max_val)
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "min_val": (
                    "INT",
                    {
                        "default": 0,
                        "min": -(2**32 - 1),
                        "max": 2**32 - 1,
                        "step": 1,
                        "display": "number",
                    },
                ),
                "max_val": (
                    "INT",
                    {
                        "default": 2**32 - 1,
                        "min": -(2**32 - 1),
                        "max": 2**32 - 1,
                        "step": 1,
                        "display": "number",
                    },
                ),
            },
        }
    RETURN_TYPES = ("INT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "System Random Int"
    @classmethod
    def IS_CHANGED(s, min_val, max_val):
       return random.SystemRandom().random()


class UUIDGenerator(RandomGuaranteedClass):
    """
    Generates a random UUID
    """
    def __init__(self):
        pass
    @staticmethod
    def generate(length=36):
        value = uuid.uuid4()
        value = str(value)
        if length < 36:
            value = value[:length]
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "length": ("INT", { "default": 36, "min": 1, "max": 36, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "UUID Generator"
    @classmethod
    def IS_CHANGED(s, length):
       return random.SystemRandom().random()

@node
class UniformRandomFloat(RandomGuaranteedClass):
    """
    Selects a random float from min to max
    Fallbacks to default if min is greater than max
    """
    def __init__(self):
        pass
    def generate(self, min_val, max_val, decimal_places, seed=0):
        if min_val > max_val:
            return min_val
        instance = random.Random(seed)
        value = instance.uniform(min_val, max_val)
        # prune to decimal places - 0 = int, 1 = 1 decimal place,...
        value = round(value, decimal_places)
        #print(f"Selected {value} from {min_val} to {max_val}")
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "min_val": ("FLOAT", { "default": 0.0, "min": -999999999, "max": 999999999.0, "step": 0.02, "display": "number" }),
                "max_val": ("FLOAT", { "default": 1.0, "min": -999999999, "max": 999999999.0, "step": 0.02, "display": "number" }),
                "decimal_places": ("INT", { "default": 1, "min": 0, "max": 10, "step": 1, "display": "number" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Uniform Random Float"
    
@node
class UniformRandomInt(RandomGuaranteedClass):
    """
    Selects a random int from min to max
    Fallbacks to default if min is greater than max
    """
    def __init__(self):
        pass
    def generate(self, min_val, max_val, seed=0):
        if min_val > max_val:
            return min_val
        instance = random.Random(seed)
        value = instance.randint(min_val, max_val)
        #print(f"Selected {value} from {min_val} to {max_val}")
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "min_val": ("INT", { "default": 0, "min": -999999999, "max": 999999999, "step": 1, "display": "number" }),
                "max_val": ("INT", { "default": 1, "min": -999999999, "max": 999999999, "step": 1, "display": "number" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("INT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Uniform Random Int"
@node
class UniformRandomChoice(RandomGuaranteedClass):
    """
    Parses input string with separator '$' and returns a random choice
    separator can be changed in the input
    """
    def __init__(self):
        pass
    def generate(self, input_string, separator, seed=0):
        instance = random.Random(seed)
        choices = input_string.split(separator)
        value = instance.choice(choices)
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "a$b$c", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Uniform Random Choice"
@node
class ManualChoiceString:
    """
    Parses input string with separator '$' and returns a random choice
    separator can be changed in the input
    Accepts index of choice as input
    """
    def __init__(self):
        pass
    def generate(self, input_string, separator, index):
        choices = input_string.split(separator)
        value = choices[index]
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "a$b$c", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "index": ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Manual Choice String"
@node
class ManualChoiceInt:
    """
    Parses input string with separator '$' and returns a random choice
    Returns as int
    separator can be changed in the input
    Accepts index of choice as input
    """
    def __init__(self):
        pass
    def generate(self, input_string, separator, index):
        choices = input_string.split(separator)
        value = int(choices[index])
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "1$2$3", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "index": ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("INT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Manual Choice Int"
@node
class ManualChoiceFloat:
    """
    Parses input string with separator '$' and returns a random choice
    Returns as float
    separator can be changed in the input
    Accepts index of choice as input
    """
    def __init__(self):
        pass
    def generate(self, input_string, separator, index):
        choices = input_string.split(separator)
        value = float(choices[index])
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "1.0$2.0$3.0", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "index": ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Manual Choice Float"

@node
class RandomShuffleInt(RandomGuaranteedClass):
    """
    Get the shuffled list of integers from start to end
    Input types and output types are lists of ints
    """
    def __init__(self):
        pass
    def generate(self, input_string, separator, seed=0):
        instance = random.Random(seed)
        choices = input_string.split(separator)
        # shuffle the list
        instance.shuffle(choices)
        return (choices,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "1$2$3", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Random Shuffle Int"
@node
class RandomShuffleFloat(RandomGuaranteedClass):
    """
    Get the shuffled list of floats from start to end
    Input types and output types are lists of floats
    """
    def __init__(self):
        pass
    def generate(self, input_string, separator, seed=0):
        instance = random.Random(seed)
        choices = input_string.split(separator)
        # shuffle the list
        instance.shuffle(choices)
        return (choices,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "1.0$2.0$3.0", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Random Shuffle Float"
@node
class RandomShuffleString(RandomGuaranteedClass):
    """
    Get the shuffled list of strings from start to end
    Input types and output types are lists of strings
    """
    def __init__(self):
        pass
    def generate(self, input_string, separator, seed=0):
        instance = random.Random(seed)
        choices = input_string.split(separator)
        # shuffle the list
        instance.shuffle(choices)
        return (choices,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "a$b$c", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Random Shuffle String"

@node
class YieldableIteratorString:
    """
    Yields sequentially from the input list (with separator)
    If reset is True, then it starts from the beginning
    """
    def __init__(self):
        self.index = 0
    def generate(self, input_string, separator, reset):
        choices = input_string.split(separator)
        if reset:
            self.index = 0
        else:
            self.index += 1
        if self.index >= len(choices):
            self.index = 0
        value = choices[self.index]
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_string": ("STRING", { "default": "a$b$c", "display": "text" }),
                "separator": ("STRING", { "default": "$", "display": "text" }),
                "reset": ("INT", { "default": 0, "min": 0, "max": 1, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Yieldable Iterator String"

@node
class YieldableIteratorInt:
    """
    Yields sequentially with start, end, step
    Resets if reset is True
    """
    RETURN_TYPES = ("INT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"
    custom_name = "Yieldable (Sequential) Iterator Int"
    def __init__(self):
        self.iterator = None
    def generate(self, start, end, step, reset):
        if reset:
            self.iterator = None
        if self.iterator is None:
            self.iterator = range(start, end, step)
        try:
            value = next(self.iterator)
        except StopIteration:
            self.iterator = range(start, end, step)
            value = next(self.iterator)
        return (value,)
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "start": ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
                "end": ("INT", { "default": 10, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
                "step": ("INT", { "default": 1, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
                "reset": ("INT", { "default": 0, "min": 0, "max": 1, "step": 1, "display": "number" }),
            },
        }

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(classes)
validate(classes)
