import json
import os

from .autonode import node_wrapper, get_node_names_mappings, validate, anytype

##############################################################################
# "NewPointer" BASE CLASS
##############################################################################

class NewPointer:
    """A base class that forces ComfyUI to skip caching by returning NaN in IS_CHANGED."""
    RESULT_NODE = True  # Typically means the node can appear as a "result" in the graph
    OUTPUT_NODE = True  # Typically means the node can appear as an "output" in the graph
    @classmethod
    def IS_CHANGED(cls, *args, **kwargs):
        return float("NaN")  # Forces ComfyUI to consider it always changed

##############################################################################
#  HELPER: Throw if path tries to escape
##############################################################################

def throw_if_parent_or_root_access(path):
    if ".." in path or path.startswith("/") or path.startswith("\\"):
        raise RuntimeError("Tried to access parent or root directory")
    if path.startswith("~"):
        raise RuntimeError("Tried to access home directory")
    if os.path.isabs(path):
        raise RuntimeError("Path cannot be absolute")

##############################################################################
# REGISTER CLASSES BELOW
##############################################################################

fundamental_classes = []
fundamental_node = node_wrapper(fundamental_classes)

############################
#  GLOBALS & JSON NODES
############################

GLOBAL_STORAGE = {}  # For global variable set/get

@fundamental_node
class JsonParseNode(NewPointer):
    """
    Convert JSON string into a Python object (dict, list, etc.) stored in 'anytype'.
    """
    FUNCTION = "parse_json"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Data"
    custom_name="Pyobjects/JSON -> PyObject"

    @staticmethod
    def parse_json(json_string):
        try:
            obj = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {str(e)}")
        return (obj,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_string": ("STRING", {"default": '{"key": "value"}'}),
            }
        }

@fundamental_node
class JsonDumpNode(NewPointer):
    """
    Convert a Python object (dict, list, etc.) into a JSON string.
    """
    FUNCTION = "dump_json"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "Data"
    custom_name="Pyobjects/PyObject -> JSON"

    @staticmethod
    def dump_json(py_obj, indent=0):
        json_str = json.dumps(py_obj, indent=indent, ensure_ascii=False)
        return (json_str,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_obj": (anytype, ),
            },
            "optional": {
                "indent": ("INT", {"default": 0}),
            }
        }

@fundamental_node
class JsonDumpAnyStructureNode(NewPointer):
    """
    Dump either DICT or LIST or SET (any Python structure) into JSON string.
    """
    FUNCTION = "dump_any_struct"
    RETURN_TYPES = ("STRING",)
    CATEGORY = "Data"
    custom_name="Pyobjects/PyStructure -> JSON"

    @staticmethod
    def dump_any_struct(py_obj, indent=0):
        return (json.dumps(py_obj, indent=indent, ensure_ascii=False),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_obj": (anytype,),
            },
            "optional": {
                "indent": ("INT", {"default": 0}),
            }
        }

############################
#  DICT NODES
############################

@fundamental_node
class DictCreateNode(NewPointer):
    """
    Creates a new empty dictionary (type DICT).
    """
    FUNCTION = "create_dict"
    RETURN_TYPES = ("DICT",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Create Dict"

    @staticmethod
    def create_dict():
        return ({},)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

@fundamental_node
class DictSetNode(NewPointer):
    """
    dict[key] = value. Returns the updated dict.
    """
    FUNCTION = "dict_set"
    RETURN_TYPES = ("DICT",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Set"

    @staticmethod
    def dict_set(py_dict, key, value):
        if not isinstance(py_dict, dict):
            raise ValueError("Input must be a Python dict")
        py_dict[key] = value
        return (py_dict,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_dict": ("DICT", ),
                "key": ("STRING", {"default": "some_key"}),
                "value": (anytype, {"default": "some_value"})
            }
        }

@fundamental_node
class DictGetNode(NewPointer):
    """
    Returns dict[key]. If key not found, returns None.
    """
    FUNCTION = "dict_get"
    RETURN_TYPES = (anytype,)  # The retrieved value can be anything
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Get"

    @staticmethod
    def dict_get(py_dict, key):
        if not isinstance(py_dict, dict):
            raise ValueError("Input must be a Python dict")
        return (py_dict.get(key, None),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_dict": ("DICT", ),
                "key": ("STRING", {"default": "some_key"}),
            }
        }

@fundamental_node
class DictRemoveKeyNode(NewPointer):
    """
    Removes a key from the dictionary (if present). Returns the updated dict.
    """
    FUNCTION = "dict_remove_key"
    RETURN_TYPES = ("DICT",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Remove Key"

    @staticmethod
    def dict_remove_key(py_dict, key):
        if not isinstance(py_dict, dict):
            raise ValueError("Input must be a Python dict")
        py_dict.pop(key, None)
        return (py_dict,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_dict": ("DICT",),
                "key": ("STRING", {"default": "some_key"}),
            }
        }

@fundamental_node
class DictMergeNode(NewPointer):
    """
    Merges two dictionaries. 
    If there are duplicate keys, the second dict's values overwrite the first.
    Returns a new dictionary (or modifies the first in place, see below).
    """
    FUNCTION = "dict_merge"
    RETURN_TYPES = ("DICT",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Merge"

    @staticmethod
    def dict_merge(dict_a, dict_b, in_place=False):
        if not isinstance(dict_a, dict) or not isinstance(dict_b, dict):
            raise ValueError("Both inputs must be Python dicts")
        if in_place:
            dict_a.update(dict_b)
            return (dict_a,)
        else:
            merged = {**dict_a, **dict_b}
            return (merged,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "dict_a": ("DICT",),
                "dict_b": ("DICT",),
            },
            "optional": {
                "in_place": ("BOOLEAN", {"default": False}),
            }
        }

@fundamental_node
class DictKeysNode(NewPointer):
    """
    Returns the list of keys in a dictionary as type LIST.
    """
    FUNCTION = "dict_keys"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Keys"

    @staticmethod
    def dict_keys(py_dict):
        if not isinstance(py_dict, dict):
            raise ValueError("Input must be a Python dict")
        keys_list = list(py_dict.keys())
        return (keys_list,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_dict": ("DICT",),
            }
        }

@fundamental_node
class DictValuesNode(NewPointer):
    """
    Returns the list of values in a dictionary as type LIST.
    """
    FUNCTION = "dict_values"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Values"

    @staticmethod
    def dict_values(py_dict):
        if not isinstance(py_dict, dict):
            raise ValueError("Input must be a Python dict")
        values_list = list(py_dict.values())
        return (values_list,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_dict": ("DICT",),
            }
        }

@fundamental_node
class DictItemsNode(NewPointer):
    """
    Returns the list of (key, value) pairs in a dictionary as type LIST.
    Each item in the list is a 2-element tuple [key, value].
    """
    FUNCTION = "dict_items"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Items"

    @staticmethod
    def dict_items(py_dict):
        if not isinstance(py_dict, dict):
            raise ValueError("Input must be a Python dict")
        items_list = list(py_dict.items())
        return (items_list,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_dict": ("DICT",),
            }
        }

@fundamental_node
class DictPointer(NewPointer):
    """
    Example of a stateful node: holds onto the incoming dict until reset.
    """
    FUNCTION = "dict_pointer"
    RETURN_TYPES = ("DICT",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Dict Pointer"

    def __init__(self):
        self.pointer = None

    def dict_pointer(self, py_dict, reset=False):
        if not isinstance(py_dict, dict):
            raise ValueError("Input must be a Python dict")
        if self.pointer is None or reset:
            self.pointer = py_dict
        if reset:
            value = self.pointer
            self.pointer = None
            return (value,)
        return (self.pointer,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_dict": ("DICT", ),
            },
            "optional": {
                "reset": ("BOOLEAN",),
            },
        }

############################
#  GLOBAL VAR NODES
############################

@fundamental_node
class GlobalVarSetNode(NewPointer):
    """
    Store a Python object in a global dictionary under the given key.
    Returns the same value that was stored, as anytype.
    """
    FUNCTION = "global_var_set"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Data"
    custom_name="Pyobjects/Global Var Set"

    def global_var_set(self, key, value):
        GLOBAL_STORAGE[key] = value
        print("GlobalVarSetNode:", GLOBAL_STORAGE)
        return (value,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "my_key"}),
                "value": (anytype, {"default": "my_value"}),
            }
        }

@fundamental_node
class GlobalVarSetIfNotExistsNode(NewPointer):
    """
    Store a Python object in a global dictionary under the given key, only if the key doesn't already exist.
    """
    FUNCTION = "global_var_set_if_not_exists"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Data"
    custom_name="Pyobjects/Global Var Set If Not Exists"

    def global_var_set_if_not_exists(self, key, value):
        if key not in GLOBAL_STORAGE:
            GLOBAL_STORAGE[key] = value
        print("GlobalVarSetIfNotExistsNode:", GLOBAL_STORAGE)
        return (GLOBAL_STORAGE[key],)  # Return the final stored value

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "my_key"}),
                "value": (anytype, {"default": "my_value"}),
            }
        }

@fundamental_node
class GlobalVarGetNode(NewPointer):
    """
    Retrieve a Python object from the global dictionary by key.
    If not found, returns None by default.
    """
    FUNCTION = "global_var_get"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Data"
    custom_name="Pyobjects/Global Var Get"

    def global_var_get(self, key):
        print("GlobalVarGetNode:", GLOBAL_STORAGE)
        return (GLOBAL_STORAGE.get(key, None),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "my_key"}),
            }
        }

@fundamental_node
class GlobalVarRemoveNode(NewPointer):
    """
    Remove a key from the global dictionary (if present).
    Returns the value that was removed, or None if key didn't exist.
    """
    FUNCTION = "global_var_remove"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Data"
    custom_name="Pyobjects/Global Var Remove"

    def global_var_remove(self, key):
        removed_value = GLOBAL_STORAGE.pop(key, None)
        return (removed_value,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "my_key"}),
            }
        }

@fundamental_node
class GlobalVarSaveNode(NewPointer):
    """
    Saves the value of GLOBAL_STORAGE[key] to a JSON file on disk.
    If the key isn't in storage, returns an error or saves None if allow_missing=True.
    """
    FUNCTION = "global_var_save"
    RETURN_TYPES = ("STRING",)  # Return the filepath that was saved
    CATEGORY = "Data"
    custom_name="Pyobjects/Global Var Save"

    def global_var_save(self, key, filepath, allow_missing=False):
        throw_if_parent_or_root_access(filepath)

        value = GLOBAL_STORAGE.get(key, None)
        if value is None and not allow_missing and key not in GLOBAL_STORAGE:
            raise KeyError(f"Global key '{key}' not found in storage. Set allow_missing=True to save None.")

        dir_ = os.path.dirname(filepath)
        if dir_ and not os.path.exists(dir_):
            os.makedirs(dir_, exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=4)
        return (filepath,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "my_key"}),
                "filepath": ("STRING", {"default": "my_global_var.json"}),
            },
            "optional": {
                "allow_missing": ("BOOLEAN", {"default": False})
            }
        }

@fundamental_node
class GlobalVarLoadNode(NewPointer):
    """
    Loads JSON from a file and stores it in GLOBAL_STORAGE under the given key.
    Returns the loaded value.
    """
    FUNCTION = "global_var_load"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Data"
    custom_name="Pyobjects/Global Var Load"

    def global_var_load(self, key, filepath, allow_missing=False):
        throw_if_parent_or_root_access(filepath)

        if not os.path.exists(filepath):
            if allow_missing:
                GLOBAL_STORAGE[key] = None
                return (None,)
            else:
                raise FileNotFoundError(f"File '{filepath}' does not exist.")

        with open(filepath, "r", encoding="utf-8") as f:
            value = json.load(f)
        GLOBAL_STORAGE[key] = value
        return (value,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "key": ("STRING", {"default": "my_key"}),
                "filepath": ("STRING", {"default": "my_global_var.json"}),
            },
            "optional": {
                "allow_missing": ("BOOLEAN", {"default": False}),
            }
        }

############################
#  LIST NODES
############################

@fundamental_node
class ListCreateNode(NewPointer):
    """
    Creates a new empty list (type LIST).
    """
    FUNCTION = "create_list"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Create List"

    @staticmethod
    def create_list():
        return ([],)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

@fundamental_node
class ListAppendNode(NewPointer):
    """
    Append an item to a Python list. Returns the updated list.
    """
    FUNCTION = "list_append"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/List Append"

    @staticmethod
    def list_append(py_list, item):
        if not isinstance(py_list, list):
            raise ValueError("Input must be a Python list")
        py_list.append(item)
        return (py_list,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_list": ("LIST",),
                "item": (anytype,),
            }
        }

@fundamental_node
class ListGetNode(NewPointer):
    """
    Return an element from a list by index as anytype.
    """
    FUNCTION = "list_get"
    RETURN_TYPES = (anytype,)
    CATEGORY = "Data"
    custom_name="Pyobjects/List Get"

    @staticmethod
    def list_get(py_list, index):
        if not isinstance(py_list, list):
            raise ValueError("Input must be a Python list")
        if index < 0 or index >= len(py_list):
            raise IndexError("Index out of range")
        return (py_list[index],)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_list": ("LIST",),
                "index": ("INT", {"default": 0}),
            }
        }

@fundamental_node
class ListRemoveNode(NewPointer):
    """
    Removes the first occurrence of 'item' from the list (if present).
    Returns the updated list.
    """
    FUNCTION = "list_remove"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/List Remove"

    @staticmethod
    def list_remove(py_list, item):
        if not isinstance(py_list, list):
            raise ValueError("Input must be a Python list")
        if item in py_list:
            py_list.remove(item)
        return (py_list,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_list": ("LIST",),
                "item": (anytype,),
            }
        }

@fundamental_node
class ListPopNode(NewPointer):
    """
    Pop an item from the list by index. 
    Returns (popped_item, updated_list).
    """
    FUNCTION = "list_pop"
    RETURN_TYPES = (anytype, "LIST")
    CATEGORY = "Data"
    custom_name="Pyobjects/List Pop"

    @staticmethod
    def list_pop(py_list, index=-1):
        if not isinstance(py_list, list):
            raise ValueError("Input must be a Python list")
        if len(py_list) == 0:
            raise IndexError("Cannot pop from an empty list")
        popped = py_list.pop(index)
        return (popped, py_list)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_list": ("LIST",),
            },
            "optional": {
                "index": ("INT", {"default": -1}),
            }
        }

@fundamental_node
class ListInsertNode(NewPointer):
    """
    Insert an item into the list at a given index.
    Returns the updated list.
    """
    FUNCTION = "list_insert"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/List Insert"

    @staticmethod
    def list_insert(py_list, index, item):
        if not isinstance(py_list, list):
            raise ValueError("Input must be a Python list")
        py_list.insert(index, item)
        return (py_list,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_list": ("LIST",),
                "index": ("INT", {"default": 0}),
                "item": (anytype,),
            }
        }

@fundamental_node
class ListExtendNode(NewPointer):
    """
    Extends list A by appending elements from list B. Returns the updated list A.
    """
    FUNCTION = "list_extend"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/List Extend"

    @staticmethod
    def list_extend(list_a, list_b):
        if not isinstance(list_a, list) or not isinstance(list_b, list):
            raise ValueError("Both inputs must be Python lists")
        list_a.extend(list_b)
        return (list_a,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "list_a": ("LIST",),
                "list_b": ("LIST",),
            }
        }

@fundamental_node
class ToListTypeNode(NewPointer):
    """
    Takes any Python object that is actually iterable, returns it as type LIST.
    (Casts dicts/sets/tuples to list by calling list(obj).)
    """
    FUNCTION = "to_list_type"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Cast to LIST"

    @staticmethod
    def to_list_type(py_obj):
        if isinstance(py_obj, dict):
            # e.g. we can choose to return keys or something else
            return (list(py_obj.keys()),)
        try:
            return (list(py_obj),)
        except TypeError:
            raise ValueError("Object is not iterable, cannot cast to list")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_obj": (anytype,),
            }
        }

############################
#  SET NODES
############################

@fundamental_node
class ToSetTypeNode(NewPointer):
    """
    Takes any Python object that is iterable, returns it as type SET.
    (Casts dict/list/tuple to set(obj). For dict, uses dict.keys().)
    """
    FUNCTION = "to_set_type"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Cast to SET"

    @staticmethod
    def to_set_type(py_obj):
        if isinstance(py_obj, dict):
            return (set(py_obj.keys()),)
        try:
            return (set(py_obj),)
        except TypeError:
            raise ValueError("Object is not iterable, cannot cast to set")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_obj": (anytype,),
            }
        }

@fundamental_node
class SetCreateNode(NewPointer):
    """
    Creates a new empty set (type SET).
    """
    FUNCTION = "create_set"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Create Set"

    @staticmethod
    def create_set():
        return (set(),)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

@fundamental_node
class SetAddNode(NewPointer):
    """
    Adds an item to a set.
    """
    FUNCTION = "set_add"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set Add"

    @staticmethod
    def set_add(py_set, item):
        if not isinstance(py_set, set):
            raise ValueError("Input must be a Python set")
        py_set.add(item)
        return (py_set,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set": ("SET",),
                "item": (anytype,),
            }
        }

@fundamental_node
class SetRemoveNode(NewPointer):
    """
    Removes an item from the set (if present).
    """
    FUNCTION = "set_remove"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set Remove"

    @staticmethod
    def set_remove(py_set, item):
        if not isinstance(py_set, set):
            raise ValueError("Input must be a Python set")
        py_set.discard(item)
        return (py_set,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set": ("SET",),
                "item": (anytype,),
            }
        }

@fundamental_node
class SetUnionNode(NewPointer):
    """
    Returns the union of two sets.
    """
    FUNCTION = "set_union"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set Union"

    @staticmethod
    def set_union(py_set_a, py_set_b):
        if not isinstance(py_set_a, set) or not isinstance(py_set_b, set):
            raise ValueError("Both inputs must be Python sets")
        return (py_set_a.union(py_set_b),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set_a": ("SET",),
                "py_set_b": ("SET",),
            }
        }

@fundamental_node
class SetIntersectionNode(NewPointer):
    """
    Returns the intersection of two sets.
    """
    FUNCTION = "set_intersection"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set Intersection"

    @staticmethod
    def set_intersection(py_set_a, py_set_b):
        if not isinstance(py_set_a, set) or not isinstance(py_set_b, set):
            raise ValueError("Both inputs must be Python sets")
        return (py_set_a.intersection(py_set_b),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set_a": ("SET",),
                "py_set_b": ("SET",),
            }
        }

@fundamental_node
class SetDifferenceNode(NewPointer):
    """
    Returns the difference of two sets: A - B.
    """
    FUNCTION = "set_difference"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set Difference"

    @staticmethod
    def set_difference(py_set_a, py_set_b):
        if not isinstance(py_set_a, set) or not isinstance(py_set_b, set):
            raise ValueError("Both inputs must be Python sets")
        return (py_set_a.difference(py_set_b),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set_a": ("SET",),
                "py_set_b": ("SET",),
            }
        }

@fundamental_node
class SetSymDifferenceNode(NewPointer):
    """
    Returns the symmetric difference (elements in A or B but not both).
    """
    FUNCTION = "set_sym_difference"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set Symmetric Difference"

    @staticmethod
    def set_sym_difference(py_set_a, py_set_b):
        if not isinstance(py_set_a, set) or not isinstance(py_set_b, set):
            raise ValueError("Both inputs must be Python sets")
        return (py_set_a.symmetric_difference(py_set_b),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set_a": ("SET",),
                "py_set_b": ("SET",),
            }
        }

@fundamental_node
class SetClearNode(NewPointer):
    """
    Clears all elements from the set. Returns the now-empty set.
    """
    FUNCTION = "set_clear"
    RETURN_TYPES = ("SET",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set Clear"

    @staticmethod
    def set_clear(py_set):
        if not isinstance(py_set, set):
            raise ValueError("Input must be a Python set")
        py_set.clear()
        return (py_set,)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set": ("SET",),
            }
        }

@fundamental_node
class SetToListNode(NewPointer):
    """
    Converts a set to a list. Returns the list as type LIST.
    """
    FUNCTION = "set_to_list"
    RETURN_TYPES = ("LIST",)
    CATEGORY = "Data"
    custom_name="Pyobjects/Set to List"

    @staticmethod
    def set_to_list(py_set):
        if not isinstance(py_set, set):
            raise ValueError("Input must be a Python set")
        return (list(py_set),)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "py_set": ("SET",),
            }
        }

##############################################################################
# REGISTER THE NODES
##############################################################################

CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(fundamental_classes)
validate(fundamental_classes)
