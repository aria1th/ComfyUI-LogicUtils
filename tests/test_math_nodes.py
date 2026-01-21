import unittest
from unittest.mock import patch

from import_utils import import_local


class TestMathNodes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.math_nodes = import_local("math_nodes")

    def test_power_allows_one_and_zero(self):
        Power = self.math_nodes.CLASS_MAPPINGS["PowerNode"]
        node = Power()
        self.assertEqual(node.power(1, 5), (1.0,))
        self.assertEqual(node.power(0, 2), (0.0,))
        self.assertEqual(node.power(0, 0), (1.0,))
        with self.assertRaises(ZeroDivisionError):
            node.power(0, -1)

    def test_power_overflow_guard(self):
        Power = self.math_nodes.CLASS_MAPPINGS["PowerNode"]
        node = Power()
        with self.assertRaises(OverflowError):
            node.power(10, 101)

    def test_modulo_node_is_registered(self):
        self.assertIn("ModuloNode", self.math_nodes.CLASS_MAPPINGS)
        Modulo = self.math_nodes.CLASS_MAPPINGS["ModuloNode"]
        self.assertEqual(Modulo().modulo(10, 3), (1,))

    def test_is_prime_small(self):
        is_prime_small = self.math_nodes.is_prime_small
        self.assertFalse(is_prime_small(0))
        self.assertFalse(is_prime_small(1))
        self.assertTrue(is_prime_small(2))
        self.assertTrue(is_prime_small(3))
        self.assertFalse(is_prime_small(4))
        self.assertTrue(is_prime_small(7919))

    def test_is_prime_miller_rabin_deterministic_seed(self):
        is_prime_miller_rabin = self.math_nodes.is_prime_miller_rabin
        # Force a deterministic base for stable tests.
        with patch("random.randrange", return_value=2):
            self.assertTrue(is_prime_miller_rabin(1_000_000_007, k=3))
            self.assertFalse(is_prime_miller_rabin(1517, k=3))
