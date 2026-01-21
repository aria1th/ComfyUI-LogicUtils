import unittest

import numpy as np
import torch
from Crypto.PublicKey import RSA

from import_utils import import_local


class TestCryptoNodes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.crypto = import_local("crypto")

    def test_encrypt_decrypt_roundtrip(self):
        Encrypt = self.crypto.CLASS_MAPPINGS["SecureBase64Encrypt"]
        Decrypt = self.crypto.CLASS_MAPPINGS["SecureWebPDecrypt"]

        key = RSA.generate(1024)
        private_pem = key.export_key().decode("utf-8")
        public_pem = key.publickey().export_key().decode("utf-8")

        # Create a small deterministic RGB image tensor with values aligned to 1/255.
        arr = np.zeros((8, 8, 3), dtype=np.uint8)
        arr[0, 0] = [255, 0, 0]
        arr[0, 1] = [0, 255, 0]
        arr[0, 2] = [0, 0, 255]
        img = torch.from_numpy(arr.astype(np.float32) / 255.0).unsqueeze(0)

        enc = Encrypt()
        encrypted_b64 = enc.encrypted_base64(img, public_pem)[0]
        self.assertIsInstance(encrypted_b64, str)

        dec = Decrypt()
        decrypted = dec.decrypt_image(encrypted_b64, private_pem)[0]
        self.assertTrue(torch.is_tensor(decrypted))
        self.assertEqual(tuple(decrypted.shape), tuple(img.shape))
        self.assertTrue(torch.allclose(decrypted, img, atol=1 / 255, rtol=0))
