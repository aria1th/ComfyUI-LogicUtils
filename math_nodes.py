import random
from .autonode import node_wrapper, get_node_names_mappings, validate, anytype
classes = []
node = node_wrapper(classes)
import math

@node
class MinNode:
    """
    Returns the minimum of two values
    """
    RETURN_TYPES = (anytype,)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
            "input2": (anytype,),
        }
    }
    FUNCTION = "min"
    CATEGORY = "Math"
    custom_name = "Min"
    def min(self, input1, input2):
        return (min(input1, input2),)

@node
class MaxNode:
    """
    Returns the maximum of two values
    """
    RETURN_TYPES = (anytype,)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
            "input2": (anytype,),
        }
    }
    FUNCTION = "max"
    CATEGORY = "Math"
    custom_name = "Max"
    def max(self, input1, input2):
        return (max(input1, input2),)

@node
class RoundNode:
    """
    Rounds a value to the nearest integer
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
        }
    }
    FUNCTION = "round"
    CATEGORY = "Math"
    custom_name = "Round"
    def round(self, input1):
        return (round(input1),)

@node
class AbsNode:
    """
    Returns the absolute value of a number
    """
    RETURN_TYPES = (anytype,)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
        }
    }
    FUNCTION = "abs"
    CATEGORY = "Math"
    custom_name = "Abs"
    def abs(self, input1):
        return (abs(input1),)

@node
class FloorNode:
    """
    Returns the floor of a number
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
        }
    }
    FUNCTION = "floor"
    CATEGORY = "Math"
    custom_name = "Floor"
    def floor(self, input1):
        return (math.floor(input1),)

@node
class CeilNode:
    """
    Returns the ceiling of a number
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
        }
    }
    FUNCTION = "ceil"
    CATEGORY = "Math"
    custom_name = "Ceil"
    def ceil(self, input1):
        return (math.ceil(input1),)

@node
class PowerNode:
    """
    Returns the power of a number
    """
    RETURN_TYPES = (anytype,)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
            "power": (anytype,),
        }
    }
    FUNCTION = "power"
    CATEGORY = "Math"
    custom_name = "Power"
    def power(self, input1, power):
        abs_input = abs(input1)
        # fast paths for values that won't overflow digit-wise
        if abs_input == 0:
            if power < 0:
                raise ZeroDivisionError("0 cannot be raised to a negative power")
            return (math.pow(input1, power),)
        if abs_input == 1:
            return (math.pow(input1, power),)

        # validate power with log10 scale, prevent huge magnitudes
        log10_abs = math.log10(abs_input)
        if (log10_abs * power) > 100:
            raise OverflowError("Power is too large, exceeds 100 digits")
        return (math.pow(input1, power),)

@node
class SigmoidNode:
    """
    Returns the sigmoid of a number
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT",),
        }
    }
    FUNCTION = "sigmoid"
    CATEGORY = "Math"
    custom_name = "Sigmoid"
    def sigmoid(self, input1):
        return (1 / (1 + math.exp(-input1)),)
def is_prime_small(n: int) -> bool:
    """
    Deterministic check for primality for smaller n.
    Skips multiples of 2 and 3, then checks i, i+2, i+4 up to sqrt(n).
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0 or n % 3 == 0:
        return n == 2 or n == 3
    
    # 6k ± 1 optimization
    limit = int(math.isqrt(n))  # integer sqrt
    i = 5
    while i <= limit:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

def miller_rabin_test(d: int, n: int) -> bool:
    """ One round of the Miller-Rabin test with a random base 'a'. """
    a = random.randrange(2, n - 1)
    x = pow(a, d, n)  # a^d % n
    if x == 1 or x == n - 1:
        return True
    
    # Keep squaring x while d does not reach n-1
    while d != n - 1:
        x = (x * x) % n
        d <<= 1  # d *= 2
        if x == 1:
            return False
        if x == n - 1:
            return True
    return False

def is_prime_miller_rabin(n: int, k: int = 5) -> bool:
    """
    Miller-Rabin primality test with k rounds (probabilistic).
    Good enough for big integers in practice.
    """
    # Handle small or trivial cases
    if n < 2:
        return False
    # check small primes quickly
    for small_prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]:
        if n == small_prime:
            return True
        if n % small_prime == 0 and n != small_prime:
            return False

    # Write n - 1 as d * 2^r
    d = n - 1
    while d % 2 == 0:
        d //= 2

    # Witness loop
    for _ in range(k):
        if not miller_rabin_test(d, n):
            return False
    return True

@node
class IsPrimeNode:
    """
    Checks if an integer is prime.

    - If the integer |value| < threshold, uses a deterministic small-check (trial division).
    - Otherwise, uses a Miller-Rabin pseudoprime test for a faster check (probabilistic).

    Returns a BOOLEAN (True if prime, False if composite).
    """
    FUNCTION = "is_prime"
    RETURN_TYPES = ("BOOLEAN",)
    CATEGORY = "Math"
    custom_name = "Is Prime?"

    @staticmethod
    def is_prime(value: int, threshold: int = 10_000_000, miller_rabin_rounds: int = 5):
        # handle negative or zero
        if value < 2:
            return (False,)

        if value < threshold:
            # use small prime check
            return (is_prime_small(value),)
        else:
            # use Miller-Rabin
            return (is_prime_miller_rabin(value, k=miller_rabin_rounds),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "value": ("INT", {"default": 1, "min": -9999999999, "max": 9999999999, "step": 1}),
            },
            "optional": {
                "threshold": ("INT", {"default": 10_000_000, "min": 1, "max": 9999999999, "step": 1}),
                "miller_rabin_rounds": ("INT", {"default": 5, "min": 1, "max": 50, "step": 1}),
            }
        }
@node
class RAMPNode:
    """
    Returns the ramp of a number
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT",),
        }
    }
    FUNCTION = "ramp"
    CATEGORY = "Math"
    custom_name = "RAMP"
    def ramp(self, input1):
        return (max(0, input1),)

@node
class ModuloNode:
    """
    Returns the modulo of a number
    """
    RETURN_TYPES = ("INT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("INT",),
            "modulo": ("INT",),
        }
    }
    FUNCTION = "modulo"
    CATEGORY = "Math"
    custom_name = "Modulo"
    def modulo(self, input1, modulo):
        return (input1 % modulo,)

@node
class LogNode:
    """
    Returns the log of a number
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": ("FLOAT",),
            "base": ("FLOAT",),
        }
    }
    FUNCTION = "log"
    CATEGORY = "Math"
    custom_name = "Log"
    def log(self, input1, base):
        return (math.log(input1, base),)

@node
class MultiplyNode:
    """
    Returns the product of two numbers
    """
    RETURN_TYPES = (anytype,)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
            "input2": (anytype,),
        }
    }
    FUNCTION = "multiply"
    CATEGORY = "Math"
    custom_name = "Multiply"
    def multiply(self, input1, input2):
        return (input1 * input2,)

@node
class DivideNode:
    """
    Returns the quotient of two numbers
    """
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def INPUT_TYPES(s):
        return {
        "required": {
            "input1": (anytype,),
            "input2": (anytype,),
        }
    }
    FUNCTION = "divide"
    CATEGORY = "Math"
    custom_name = "Divide"
    def divide(self, input1, input2):
        if input2 == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return (input1 / input2,)

validate(classes)
CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(classes)
