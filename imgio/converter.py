from typing import Union, List
from PIL import Image
import numpy as np
import base64
import torch
import requests
import os
from io import BytesIO
import gzip
import re
from urllib.parse import urlparse


def handle_rgba_composite(
    image: Image.Image, background_color=(255, 255, 255), as_rgba=False
) -> Image.Image:
    """
    Convert RGBA image to RGB image using alpha_composite.
    """
    mode = image.mode
    if as_rgba:
        return image.convert("RGBA") # universal format
    if mode == "RGB":
        return image
    if mode == "RGBA":
        # Create a white RGBA background
        background = Image.new("RGBA", image.size, (255, 255, 255, 255))
        # Composite the original image over the white background
        composed = Image.alpha_composite(background, image)
        # Convert back to RGB (now that background is flattened)
        return composed.convert("RGB")
    elif mode == "LA":
        # "LA" is 8-bit grayscale + alpha.
        rgba_image = image.convert("RGBA")
        background = Image.new("RGBA", rgba_image.size, (*background_color, 255))
        composed = Image.alpha_composite(background, rgba_image)
        return composed.convert("RGB")

    # 3. "L" or "1" = Grayscale or Black/White, "P" = Palette
    elif mode in ["L", "1", "P"]:
        # Simply converting to "RGB" is usually enough.
        return image.convert("RGB")

    # 4. "CMYK", "YCbCr", "HSV", etc.
    elif mode in ["CMYK", "YCbCr", "HSV"]:
        # Typically, a .convert("RGB") is enough if you just need an RGB version.
        return image.convert("RGB")
    print(f"Warning: Unhandled image mode: {mode}. Converting to RGB.")
    return image.convert("RGB")

def fetch_image_securely(image_url: str,
                        allowed_schemes=('http', 'https'),
                        max_file_size=5_000_000,
                        request_timeout=30):
    """
    Fetches an image from the given URL securely.

    This function:
    1. Validates the URL scheme (only http/https).
    2. Blocks private IP/loopback addresses to prevent SSRF attacks.
    3. Streams data to avoid excessive memory usage.
    4. Checks MIME type, size limits, and optionally handles form-encoded image data.

    :param image_url: URL of the image to retrieve (e.g., an S3-signed URL).
    :param allowed_schemes: A tuple of allowed URL schemes (default: ('http', 'https')).
    :param max_file_size: Max size (in bytes) of the file to download.
    :param request_timeout: Timeout (in seconds) for the request.
    :return: PIL Image object if successful, else raises an exception.
    """

    # -- 1. Validate scheme to avoid unexpected protocols  --
    parsed = urlparse(image_url)
    if parsed.scheme not in allowed_schemes:
        raise ValueError(f"Invalid or disallowed URL scheme: {parsed.scheme}")

    # -- 2. Prevent local network (SSRF) attacks by blocking private or loopback addresses  --
    #    This is a simplified check. Consider using a library for robust IP parsing if needed.
    ip_like_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    hostname = parsed.hostname
    if (
        hostname is None
        or hostname.lower() in ("localhost", "127.0.0.1", "::1")
        or (re.match(ip_like_pattern, hostname) and hostname.startswith("10."))
        or hostname.startswith("192.168.")
        or hostname.startswith("172.16.")
        or hostname.startswith("172.17.")
        or hostname.startswith("172.18.")
        or hostname.startswith("172.19.")
        or hostname.startswith("172.2")  # covers 172.20 - 172.31
        or hostname.startswith("172.3")
    ):
        raise ValueError("URL resolves to a private or loopback address, which is disallowed.")

    # -- 3. Retrieve the response with a timeout and stream  --
    #    This handles the S3 URL just like any other public HTTPS link.
    with requests.get(image_url, timeout=request_timeout, stream=True) as response:
        response.raise_for_status()

        # -- 4. Check Content-Type in headers  --
        content_type = response.headers.get('Content-Type', '').lower()

        # If it's a direct image...
        if content_type.startswith("image/"):
            # -- 5. Check Content-Length against max_file_size  --
            content_length = response.headers.get('Content-Length')
            if content_length and int(content_length) > max_file_size:
                raise ValueError(
                    f"File is too large: {int(content_length)} bytes. "
                    f"Max allowed is {max_file_size} bytes."
                )

            data = BytesIO()
            downloaded = 0
            chunk_size = 8192
            for chunk in response.iter_content(chunk_size=chunk_size):
                downloaded += len(chunk)
                if downloaded > max_file_size:
                    raise ValueError(
                        f"File exceeded the maximum allowed size of {max_file_size} bytes."
                    )
                data.write(chunk)

            # Reset the buffer and open with PIL
            data.seek(0)
            return Image.open(data)

        # If the server reports x-www-form-urlencoded, parse for embedded image data
        elif content_type == "application/x-www-form-urlencoded":
            # let PIL handle the parsing
            try:
                return Image.open(BytesIO(response.content))
            except Exception as e:
                raise ValueError(
                    f"Failed to parse x-www-form-urlencoded data as image: {e}"
                )

        else:
            # Some other content type we don't handle
            raise ValueError(
                f"Unsupported Content-Type or not an image: {content_type}"
            )

class IOConverter:
    """
    Classify the input data type.

    Assumes the inputs to be following:

    - PIL Image
    - numpy array
    - torch tensor
    - string (path to image)
    - base64 string (which can be decoded to bytes and then to image)
    - gzip-compressed base64 string
    - URL (which can be downloaded to image)

    Do NOT pass unsafe URLs / base64 strings, as it may cause security issues.
    """

    class InputType:
        PIL = "PIL"
        NUMPY = "NUMPY"
        TORCH = "TORCH"
        STRING = "STRING"
        BASE64 = "BASE64"
        GZIP_BASE64 = "GZIP_BASE64"
        URL = "URL"

    def __init__(self):
        raise Exception("This class should not be instantiated.")

    @staticmethod
    def classify(input_data):
        if isinstance(input_data, Image.Image):
            return IOConverter.InputType.PIL
        elif isinstance(input_data, np.ndarray):
            return IOConverter.InputType.NUMPY
        elif isinstance(input_data, torch.Tensor):
            return IOConverter.InputType.TORCH
        elif isinstance(input_data, str):
            if os.path.isfile(input_data):
                return IOConverter.InputType.STRING
            elif input_data.startswith("data:image/"):
                return IOConverter.InputType.BASE64
            elif input_data.startswith("http://") or input_data.startswith("https://"):
                return IOConverter.InputType.URL
            else:
                # Attempt to detect base64-encoded data
                try:
                    decoded_data = base64.b64decode(input_data, validate=True)
                    # Check for gzip magic number
                    if decoded_data[:2] == b'\x1f\x8b':
                        return IOConverter.InputType.GZIP_BASE64
                    else:
                        return IOConverter.InputType.BASE64
                except Exception:
                    raise Exception(f"Invalid string input, cannot be decoded as base64.")
        else:
            raise Exception(f"Invalid input type, {type(input_data)}")
    @staticmethod
    def match_dtype(array_or_tensor, is_tensor=False):
        # if all value is between 0 and 1, multiply by 255 and convert to uint8
        # however already uint8, skip
        # check dtype first
        if array_or_tensor.dtype == np.uint8 or array_or_tensor.dtype == torch.uint8:
            return array_or_tensor

        if array_or_tensor.min() >= 0 and array_or_tensor.max() <= 1:
            multiplied = array_or_tensor * 255
            if not is_tensor:
                return multiplied.astype(np.uint8)
            else:
                return multiplied.to(torch.uint8)
        return array_or_tensor

    @staticmethod
    def convert_to_pil(input_data):
        input_type = IOConverter.classify(input_data)
        if input_type == IOConverter.InputType.PIL:
            return handle_rgba_composite(input_data)
        elif input_type == IOConverter.InputType.NUMPY:
            # [1, 1216, 832, 3], '<f4'] -> [1216, 832, 3], 'uint8'
            # if not first element is 1, then it is a batch of images so warning
            if input_data.shape[0] != 1:
                result = []
                for i in range(input_data.shape[0]):
                    np_array = IOConverter.match_dtype(input_data[i])
                    result.append(handle_rgba_composite(Image.fromarray(np_array)))
                return result # return list of PIL images
            input_data = IOConverter.match_dtype(input_data[0])
            return handle_rgba_composite(Image.fromarray(input_data))
        elif input_type == IOConverter.InputType.TORCH:
            # same as above
            if input_data.shape[0] != 1:
                result = []
                for i in range(input_data.shape[0]):
                    np_array = (
                        IOConverter.match_dtype(input_data[i], is_tensor=True)
                        .cpu()
                        .numpy()
                    )
                    result.append(handle_rgba_composite(Image.fromarray(np_array)))
                return result
            input_data = IOConverter.match_dtype(input_data[0], is_tensor=True)
            np_array = input_data.cpu().numpy()
            return handle_rgba_composite(Image.fromarray(np_array))
        elif input_type == IOConverter.InputType.STRING:
            return Image.open(input_data)
        elif input_type == IOConverter.InputType.GZIP_BASE64:
            decoded_data = IOConverter.read_base64(input_data)
            decompressed_data = gzip.decompress(decoded_data)
            partial_result = Image.open(BytesIO(decompressed_data))
            result = handle_rgba_composite(partial_result)
            return result
        elif input_type == IOConverter.InputType.BASE64:
            decoded_data = IOConverter.read_base64(input_data)
            partial_result = Image.open(BytesIO(decoded_data))
            result = handle_rgba_composite(partial_result)
            return result
        elif input_type == IOConverter.InputType.URL:
            partial_result = fetch_image_securely(input_data)
            result = handle_rgba_composite(partial_result)
            return result
        else:
            raise Exception(f"Invalid input type, {input_type}")

    @staticmethod
    def to_rgb_tensor(pil_image):
        if pil_image.mode == "I":
            pil_image = pil_image.point(lambda i: i * (1/255))  # convert to float
        pil_image = handle_rgba_composite(pil_image)
        np_array = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(np_array)
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        # assert 4-dimensional tensor, B,C,H,W
        if len(tensor.shape) != 4:
            raise Exception(f"Invalid tensor shape, expected 4-dimensional tensor, got {tensor.shape}")
        return tensor

    @staticmethod
    def to_rgba_tensor(pil_image):
        if pil_image.mode == "I":
            pil_image = pil_image.point(lambda i: i * (1/255))  # convert to float
        pil_image = handle_rgba_composite(pil_image, as_rgba=True)
        np_array = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(np_array)
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        # assert 4-dimensional tensor, B,C,H,W
        if len(tensor.shape) != 4:
            raise Exception(f"Invalid tensor shape, expected 4-dimensional tensor, got {tensor.shape}")
        return tensor

    @staticmethod
    def read_base64(base64_string: str) -> bytes:
        return base64.b64decode(base64_string)

    @staticmethod
    def read_maybe_gzip_base64(base64_string: str) -> bytes:
        decoded_data = base64.b64decode(base64_string)
        if decoded_data[:2] == b'\x1f\x8b':
            result = gzip.decompress(decoded_data)
        else:
            result = decoded_data
        # to string
        return result.decode('utf-8')

    @staticmethod
    def convert_to_rgb_tensor(input_data, rgba=False):
        if not rgba:
            output_func = IOConverter.to_rgb_tensor
        else:
            output_func = IOConverter.to_rgba_tensor
        input_type = IOConverter.classify(input_data)
        if input_type == IOConverter.InputType.PIL:
            return output_func(input_data)
        elif input_type == IOConverter.InputType.NUMPY:
            # if all values are 0~1, skip
            if input_data.min() >= 0 and input_data.max() <= 1:
                np_array = input_data.astype(np.float32)
            else:
                np_array = input_data.astype(np.float32) / 255.0
            tensor = torch.from_numpy(np_array)
            tensor = tensor.unsqueeze(0)  # Add batch dimension
            return tensor
        elif input_type == IOConverter.InputType.TORCH:
            return input_data
        elif input_type == IOConverter.InputType.STRING:
            image = Image.open(input_data)
            return output_func(image)
        elif input_type == IOConverter.InputType.GZIP_BASE64:
            image = IOConverter.convert_to_pil(input_data)
            return output_func(image)
        elif input_type == IOConverter.InputType.BASE64:
            image = IOConverter.convert_to_pil(input_data)
            return output_func(image)
        elif input_type == IOConverter.InputType.URL:
            image = fetch_image_securely(input_data)
            return output_func(image)
        else:
            raise Exception(f"Invalid input type, {input_type}")

    @staticmethod
    def convert_to_base64(input_data, format="PNG", quality=100, gzip_compress=False):
        pil_image = IOConverter.convert_to_pil(input_data)
        buffered = BytesIO()
        save_params = {'format': format}
        if format.upper() in ['JPEG', 'JPG']:
            save_params['quality'] = quality
        pil_image.save(buffered, **save_params)
        buffered.seek(0)
        if gzip_compress:
            compressed_buffer = BytesIO()
            with gzip.GzipFile(fileobj=compressed_buffer, mode='wb') as f:
                f.write(buffered.getvalue())
            compressed_buffer.seek(0)
            base64_data = base64.b64encode(compressed_buffer.getvalue()).decode('utf-8')
        else:
            base64_data = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return base64_data

    @staticmethod
    def string_to_base64(input_string, gzip_compress=False):
        if gzip_compress:
            compressed_buffer = BytesIO()
            with gzip.GzipFile(fileobj=compressed_buffer, mode='wb') as f:
                f.write(input_string.encode())
            compressed_buffer.seek(0)
            base64_data = base64.b64encode(compressed_buffer.getvalue()).decode('utf-8')
        else:
            base64_data = base64.b64encode(input_string.encode()).decode('utf-8')
        return base64_data

class PILHandlingHodes:
    @staticmethod
    def handle_input(tensor_or_image) -> Union[Image.Image, List[Image.Image]]:
        pil_image = IOConverter.convert_to_pil(tensor_or_image)
        return pil_image

    @staticmethod
    def handle_output_as_pil(pil_image: Image.Image) -> Image.Image:
        return pil_image

    @staticmethod
    def handle_output_as_tensor(pil_image: Image.Image, rgba=False) -> torch.Tensor:
        return IOConverter.convert_to_rgb_tensor(pil_image, rgba=rgba)

    @staticmethod
    def handle_output_as_rgba_tensor(pil_image: Image.Image) -> torch.Tensor:
        return IOConverter.convert_to_rgb_tensor(pil_image, rgba=True)

    @staticmethod
    def output_wrapper(func):
        def wrapped(*args, **kwargs):
            outputs = func(*args, **kwargs)
            tuples_collect = []
            for output in outputs:
                if isinstance(output, (Image.Image, torch.Tensor)):
                    tuples_collect.append(PILHandlingHodes.handle_output_as_tensor(output))
                else:
                    tuples_collect.append(output)
            return tuple(tuples_collect)
        return wrapped

    @staticmethod
    def rgba_output_wrapper(func):
        def wrapped(*args, **kwargs):
            outputs = func(*args, **kwargs)
            tuples_collect = []
            for output in outputs:
                if isinstance(output, (Image.Image, torch.Tensor)):
                    tuples_collect.append(PILHandlingHodes.handle_output_as_rgba_tensor(output))
                else:
                    tuples_collect.append(output)
            return tuple(tuples_collect)
        return wrapped

    @staticmethod
    def to_base64(anything, quality=100, format="PNG", gzip_compress=False):
        base64_data = IOConverter.convert_to_base64(anything, format=format, quality=quality, gzip_compress=gzip_compress)
        return base64_data

    @staticmethod
    def string_to_base64(input_string, gzip_compress=False):
        base64_data = IOConverter.string_to_base64(input_string, gzip_compress=gzip_compress)
        return base64_data

    @staticmethod
    def maybe_gzip_base64_to_string(base64_string):
        return IOConverter.read_maybe_gzip_base64(base64_string)
