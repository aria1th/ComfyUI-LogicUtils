import random

class UniformRandomFloat:
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
                "min_val": ("FLOAT", { "default": 0.0, "min": 0.0, "max": 1000.0, "step": 0.02, "display": "number" }),
                "max_val": ("FLOAT", { "default": 1.0, "min": 0.0, "max": 1000.0, "step": 0.02, "display": "number" }),
                "decimal_places": ("INT", { "default": 1, "min": 0, "max": 10, "step": 1, "display": "number" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("FLOAT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"

class UniformRandomInt:
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
                "min_val": ("INT", { "default": 0, "min": 0, "max": 1000, "step": 1, "display": "number" }),
                "max_val": ("INT", { "default": 1, "min": 0, "max": 1000, "step": 1, "display": "number" }),
                "seed" : ("INT", { "default": 0, "min": 0, "max": 9999999999, "step": 1, "display": "number" }),
            },
        }
    RETURN_TYPES = ("INT",)
    FUNCTION = "generate"
    CATEGORY = "Logic Gates"

class UniformRandomChoice:
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

CLASS_MAPPINGS = {
    "UniformRandomFloat": UniformRandomFloat,
    "UniformRandomInt": UniformRandomInt,
    "UniformRandomChoice": UniformRandomChoice,
    "ManualChoiceString": ManualChoiceString,
    "ManualChoiceInt": ManualChoiceInt,
    "ManualChoiceFloat": ManualChoiceFloat,
}
CLASS_NAMES = {
    "UniformRandomFloat": "Uniform Random Float",
    "UniformRandomInt": "Uniform Random Int",
    "UniformRandomChoice": "Uniform Random Choice",
    "ManualChoiceString": "Manual Choice String",
    "ManualChoiceInt": "Manual Choice Int",
    "ManualChoiceFloat": "Manual Choice Float",
}
