import unittest

from import_utils import import_local


class TestLogicGates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.logic_gates = import_local("logic_gates")

    def test_mappings_have_unique_keys(self):
        module = self.logic_gates
        self.assertEqual(len(module.CLASS_MAPPINGS), len(set(module.CLASS_MAPPINGS.keys())))
        self.assertEqual(len(module.CLASS_MAPPINGS), len(module.classes))

    def test_bitwise_shift_supports_negative_shift(self):
        Shift = self.logic_gates.CLASS_MAPPINGS["LogicGateBitwiseShift"]
        node = Shift()
        self.assertEqual(node.bitwiseShift(8, 1), (16,))
        self.assertEqual(node.bitwiseShift(8, -1), (4,))

    def test_bitwise_shift_validates_range(self):
        Shift = self.logic_gates.CLASS_MAPPINGS["LogicGateBitwiseShift"]
        node = Shift()
        with self.assertRaises(ValueError):
            node.bitwiseShift(1, 33)

    def test_compare_gate(self):
        Compare = self.logic_gates.CLASS_MAPPINGS["LogicGateCompare"]
        node = Compare()
        self.assertEqual(node.compareInt(2, 1), (True,))
        self.assertEqual(node.compareInt(1, 2), (False,))

    def test_memory_node_flip_flop(self):
        Memory = self.logic_gates.CLASS_MAPPINGS["MemoryNode"]
        node = Memory()
        self.assertEqual(node.memory("a", 0), ("a",))
        self.assertEqual(node.memory("b", 0), ("a",))
        self.assertEqual(node.memory("b", 1), ("b",))

    def test_replace_string_regex(self):
        Replace = self.logic_gates.CLASS_MAPPINGS["ReplaceString"]
        node = Replace()
        self.assertEqual(node.replace("hello", "l+", "x"), ("hexo",))
