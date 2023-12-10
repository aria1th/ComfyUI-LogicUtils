
from .logic_gates import CLASS_MAPPINGS as LogicMapping, CLASS_NAMES as LogicNames
from .randomness import CLASS_MAPPINGS as RandomMapping, CLASS_NAMES as RandomNames

NODE_CLASS_MAPPINGS = {
}
NODE_CLASS_MAPPINGS.update(LogicMapping)
NODE_CLASS_MAPPINGS.update(RandomMapping)

NODE_DISPLAY_NAME_MAPPINGS = {

}
NODE_DISPLAY_NAME_MAPPINGS.update(LogicNames)
NODE_DISPLAY_NAME_MAPPINGS.update(RandomNames)
