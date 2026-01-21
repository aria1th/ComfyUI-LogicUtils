import unittest

import numpy as np
import torch
from PIL import Image

from import_utils import import_local


class TestImgIOConverter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.converter = import_local("imgio.converter")

    def test_handle_rgba_composite_outputs_rgb(self):
        img = Image.new("RGBA", (4, 4), (255, 0, 0, 128))
        out = self.converter.handle_rgba_composite(img)
        self.assertEqual(out.mode, "RGB")

    def test_classify_pil_numpy_torch(self):
        IOConverter = self.converter.IOConverter
        img = Image.new("RGB", (2, 2), (0, 0, 0))
        arr = np.zeros((1, 2, 2, 3), dtype=np.uint8)
        ten = torch.zeros((1, 2, 2, 3), dtype=torch.float32)

        self.assertEqual(IOConverter.classify(img), IOConverter.InputType.PIL)
        self.assertEqual(IOConverter.classify(arr), IOConverter.InputType.NUMPY)
        self.assertEqual(IOConverter.classify(ten), IOConverter.InputType.TORCH)

    def test_base64_roundtrip_pil(self):
        IOConverter = self.converter.IOConverter
        img = Image.new("RGB", (3, 5), (10, 20, 30))
        b64 = IOConverter.convert_to_base64(img, format="PNG")
        out = IOConverter.convert_to_pil(b64)
        self.assertEqual(out.size, img.size)
        self.assertEqual(out.mode, "RGB")

    def test_gzip_base64_string_roundtrip(self):
        IOConverter = self.converter.IOConverter
        text = "hello world"
        b64 = IOConverter.string_to_base64(text, gzip_compress=True)
        self.assertEqual(IOConverter.read_maybe_gzip_base64(b64), text)
