import tempfile
import unittest
from pathlib import Path

import torch
from PIL import Image

from import_utils import import_local


class TestIoNodesExtras(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.io_node = import_local("io_node")

    def test_comma_rejoin_defaults(self):
        Node = self.io_node.CLASS_MAPPINGS["CommaRejoinNode"]
        self.assertEqual(Node.comma_rejoin("a,b , c"), ("a, b, c",))
        self.assertEqual(Node.comma_rejoin("  a ,  b  ,c "), ("a, b, c",))

    def test_comma_rejoin_custom_separators(self):
        Node = self.io_node.CLASS_MAPPINGS["CommaRejoinNode"]
        self.assertEqual(
            Node.comma_rejoin("a| b |c", split_separator="|", join_separator="| "),
            ("a| b| c",),
        )

    def test_random_image_from_folder(self):
        Node = self.io_node.CLASS_MAPPINGS["RandomImageFromFolderNode"]

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sub = root / "sub"
            sub.mkdir()

            img1 = root / "a.png"
            img2 = root / "b.jpg"
            img3 = sub / "c.png"

            Image.new("RGB", (8, 6), (10, 20, 30)).save(img1)
            Image.new("RGB", (8, 6), (40, 50, 60)).save(img2)
            Image.new("RGB", (8, 6), (70, 80, 90)).save(img3)

            # Non-recursive should only pick from root
            tensor, path = Node.random_image_from_folder(
                str(root), "all", False, seed=0
            )
            self.assertTrue(torch.is_tensor(tensor))
            self.assertEqual(tuple(tensor.shape), (1, 6, 8, 3))
            self.assertIn(Path(path), {img1, img2})

            # Recursive should include subfolder images
            tensor, path = Node.random_image_from_folder(str(root), "png", True, seed=0)
            self.assertTrue(torch.is_tensor(tensor))
            self.assertEqual(tuple(tensor.shape), (1, 6, 8, 3))
            self.assertIn(Path(path), {img1, img3})

