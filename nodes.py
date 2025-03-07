
from .install import initialization

initialization()

from .logic_gates import CLASS_MAPPINGS as LogicMapping, CLASS_NAMES as LogicNames
from .randomness import CLASS_MAPPINGS as RandomMapping, CLASS_NAMES as RandomNames
from .conversion import CLASS_MAPPINGS as ConversionMapping, CLASS_NAMES as ConversionNames
from .math_nodes import CLASS_MAPPINGS as MathMapping, CLASS_NAMES as MathNames
from .io_node import CLASS_MAPPINGS as IOMapping, CLASS_NAMES as IONames
from .auxilary import CLASS_MAPPINGS as AuxilaryMapping, CLASS_NAMES as AuxilaryNames
from .external import CLASS_MAPPINGS as ExternalMapping, CLASS_NAMES as ExternalNames
from .crypto import CLASS_MAPPINGS as SecureMapping, CLASS_NAMES as SecureNames


NODE_CLASS_MAPPINGS = {
}
NODE_CLASS_MAPPINGS.update(IOMapping)
NODE_CLASS_MAPPINGS.update(LogicMapping)
NODE_CLASS_MAPPINGS.update(RandomMapping)
NODE_CLASS_MAPPINGS.update(ConversionMapping)
NODE_CLASS_MAPPINGS.update(MathMapping)
NODE_CLASS_MAPPINGS.update(ExternalMapping)
NODE_CLASS_MAPPINGS.update(AuxilaryMapping)
NODE_CLASS_MAPPINGS.update(SecureMapping)


NODE_DISPLAY_NAME_MAPPINGS = {

}
NODE_DISPLAY_NAME_MAPPINGS.update(IONames)
NODE_DISPLAY_NAME_MAPPINGS.update(LogicNames)
NODE_DISPLAY_NAME_MAPPINGS.update(RandomNames)
NODE_DISPLAY_NAME_MAPPINGS.update(ConversionNames)
NODE_DISPLAY_NAME_MAPPINGS.update(MathNames)
NODE_DISPLAY_NAME_MAPPINGS.update(ExternalNames)
NODE_DISPLAY_NAME_MAPPINGS.update(AuxilaryNames)
NODE_DISPLAY_NAME_MAPPINGS.update(SecureNames)

try:
    from .pystructure import CLASS_MAPPINGS as PyStructureMapping, CLASS_NAMES as PyStructureNames
    NODE_CLASS_MAPPINGS.update(PyStructureMapping)
    NODE_DISPLAY_NAME_MAPPINGS.update(PyStructureNames)
except ImportError:
    pass
