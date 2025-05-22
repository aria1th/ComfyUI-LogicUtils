import os, io
import numpy as np
from .imgio.converter import PILHandlingHodes
from .autonode import node_wrapper, get_node_names_mappings, validate

from PIL import Image
try:
    from Crypto.PublicKey import RSA
    from Crypto.Cipher import AES, PKCS1_OAEP
    from Crypto.Random import get_random_bytes
except ImportError:
    print("Crypto library not found. Please install pycryptodome.")
    raise

import torch
from base64 import b64encode, b64decode

# List of classes to register
secure_classes = []
secure_node = node_wrapper(secure_classes)

@secure_node
class SecureBase64Encrypt:
    """
    Encrypt an image as a base64 string using RSA public key + AES.
    - images: Only the first image is used.
    - public_key_pem: RSA public key (PEM string).
    Outputs: 'encrypted_base64' string that SecureWebPDecrypt can decrypt.
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "public_key_pem": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("encrypted_base64",)
    FUNCTION = "encrypted_base64"
    CATEGORY = "image"
    custom_name = "Secure Base64 Encrypt"
    OUTPUT_NODE = True
    RESULT_NODE = True

    def encrypted_base64(self, images, public_key_pem):
        # Check input
        if images is None or not len(images) or images[0] is None:
            raise ValueError("No image provided.")
        # Load RSA public key
        rsa_key = RSA.import_key(public_key_pem)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)

        # Take first image (if there's a batch dimension, pick index [0])
        img_tensor = images[0].clone().detach()
        if img_tensor.ndim == 4:
            img_tensor = img_tensor[0]

        # Convert [0..1] float => [0..255] uint8
        img_array = (255.0 * img_tensor.clamp(0, 1).cpu().numpy()).astype("uint8")

        # If shape is (C,H,W), transpose to (H,W,C). If shape is (H,W,C), leave as is.
        if img_array.ndim == 3:
            # If the first dimension is small (1,3,4), interpret as channels-first
            if img_array.shape[0] in [1,3,4] and img_array.shape[-1] not in [1,3,4]:
                img_array = np.transpose(img_array, (1,2,0))

        # The critical fix: ensure array is contiguous
        img_array = np.ascontiguousarray(img_array)

        # Create a PIL Image from array
        pil_img = Image.fromarray(img_array, mode="RGB")

        # Save in-memory as lossless WebP
        buffer = io.BytesIO()
        pil_img.save(buffer, format="WEBP", lossless=True)
        image_bytes = buffer.getvalue()

        # Generate a random AES session key, encrypt it with RSA
        session_key = get_random_bytes(16)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt the image bytes with AES-EAX
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(image_bytes)

        # Build custom envelope
        encrypted_blob = (
            b"ENCWEBP" +
            len(enc_session_key).to_bytes(2, "big") +
            enc_session_key +
            bytes([len(cipher_aes.nonce)]) + cipher_aes.nonce +
            bytes([len(tag)]) + tag +
            ciphertext
        )

        # Base64-encode the blob
        encrypted_base64 = b64encode(encrypted_blob).decode("utf-8")

        return (encrypted_base64,)


@secure_node
class SecureWebPDecrypt:
    """
    Decrypt an encrypted WebP image (or list of them) produced by SecureBase64Encrypt.
    Returns a single IMAGE (first one).
    """
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "encrypted_base64": ("STRING", {"multiline": True, "default": ""}),
                "private_key_pem": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("Decrypted_Image",)
    FUNCTION = "decrypt_image"
    CATEGORY = "image"
    custom_name = "Secure WebP Decrypt"
    @PILHandlingHodes.output_wrapper
    def decrypt_image(self, encrypted_base64, private_key_pem):
        # Convert to list if single string
        if encrypted_base64 is None:
            encrypted_base64 = []
        if isinstance(encrypted_base64, str):
            encrypted_base64 = [encrypted_base64]
        elif not isinstance(encrypted_base64, (list, tuple)):
            raise ValueError("encrypted_base64 must be string or list/tuple.")

        # Import RSA private key
        if isinstance(private_key_pem, str):
            private_key_pem = private_key_pem.encode("utf-8")
        rsa_key = RSA.import_key(private_key_pem)
        cipher_rsa = PKCS1_OAEP.new(rsa_key)

        for b64_item in encrypted_base64:
            data = b64decode(b64_item)
            if data[:7] != b"ENCWEBP":
                raise ValueError("Invalid encrypted WebP data (missing header).")

            idx = 7
            enc_key_len = int.from_bytes(data[idx : idx + 2], "big")
            idx += 2

            enc_session_key = data[idx : idx + enc_key_len]
            idx += enc_key_len

            nonce_len = data[idx]
            idx += 1
            nonce = data[idx : idx + nonce_len]
            idx += nonce_len

            tag_len = data[idx]
            idx += 1
            tag = data[idx : idx + tag_len]
            idx += tag_len

            ciphertext = data[idx:]

            # RSA-decrypt the AES session key
            session_key = cipher_rsa.decrypt(enc_session_key)

            # AES-EAX decrypt
            cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce=nonce)
            plaintext = cipher_aes.decrypt(ciphertext)
            try:
                cipher_aes.verify(tag)
            except ValueError:
                raise ValueError("Decryption failed: data tampered or wrong key.")

            # plaintext -> PIL
            pil_img = Image.open(io.BytesIO(plaintext)).convert("RGB")
            return (pil_img, )


# Register node classes with ComfyUI
CLASS_MAPPINGS, CLASS_NAMES = get_node_names_mappings(secure_classes)
validate(secure_classes)
