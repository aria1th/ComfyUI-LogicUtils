import unittest

from import_utils import import_local


class TestConversion(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conversion = import_local("conversion")

    def test_generated_conversion_nodes_exist(self):
        expected = {
            "ConvertAny2Int",
            "ConvertAny2Float",
            "ConvertAny2Boolean",
            "ConvertAny2String",
            "ConvertAny2Dict",
            "ConvertAny2List",
            "ConvertAny2Tuple",
            "ConvertAny2Set",
        }
        self.assertTrue(expected.issubset(set(self.conversion.CLASS_MAPPINGS.keys())))

    def test_convert_combo_to_string_always_returns_string(self):
        Node = self.conversion.CLASS_MAPPINGS["ConvertComboToString"]
        node = Node()
        self.assertEqual(node.convertComboToString(["a", "b"], "|"), ("a|b",))
        self.assertEqual(node.convertComboToString([1, 2, 3], ","), ("1,2,3",))
        self.assertEqual(node.convertComboToString(123, "|"), ("123",))

    def test_string_list_to_combo(self):
        Node = self.conversion.CLASS_MAPPINGS["StringListToCombo"]
        node = Node()
        self.assertEqual(node.stringListToCombo("a$b$c", "$", 1), ("b",))
        self.assertEqual(node.stringListToCombo("abc", "$", 0), ("abc",))
