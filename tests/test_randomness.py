import unittest

from import_utils import import_local


class TestRandomness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.randomness = import_local("randomness")

    def test_uniform_random_float_fallback_is_tuple(self):
        Node = self.randomness.CLASS_MAPPINGS["UniformRandomFloat"]
        self.assertEqual(Node().generate(2.0, 1.0, 1, seed=0), (2.0,))

    def test_uniform_random_int_fallback_is_tuple(self):
        Node = self.randomness.CLASS_MAPPINGS["UniformRandomInt"]
        self.assertEqual(Node().generate(2, 1, seed=0), (2,))

    def test_triangular_random_float_fallback_is_tuple(self):
        Node = self.randomness.CLASS_MAPPINGS["TriangularRandomFloat"]
        self.assertEqual(Node().generate(2.0, 1.0, 1.5, seed=0), (2.0,))

    def test_yieldable_iterator_int_is_iterable_and_wraps(self):
        Node = self.randomness.CLASS_MAPPINGS["YieldableIteratorInt"]
        it = Node()

        self.assertEqual(it.generate(0, 3, 1, True), (0,))
        self.assertEqual(it.generate(0, 3, 1, False), (1,))
        self.assertEqual(it.generate(0, 3, 1, False), (2,))
        self.assertEqual(it.generate(0, 3, 1, False), (0,))  # wraps

    def test_yieldable_iterator_string_starts_at_first(self):
        Node = self.randomness.CLASS_MAPPINGS["YieldableIteratorString"]
        it = Node()

        self.assertEqual(it.generate("a$b$c", "$", False), ("a",))
        self.assertEqual(it.generate("a$b$c", "$", False), ("b",))
        self.assertEqual(it.generate("a$b$c", "$", True), ("a",))
