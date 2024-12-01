from PIL import Image
import numpy as np
import base64
import torch
import requests
import os
from io import BytesIO
import gzip

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
            return input_data
        elif input_type == IOConverter.InputType.NUMPY:
            # [1, 1216, 832, 3], '<f4'] -> [1216, 832, 3], 'uint8'
            # if not first element is 1, then it is a batch of images so warning
            if input_data.shape[0] != 1:
                print("Warning: Batch of images detected, taking first image")
            input_data = IOConverter.match_dtype(input_data[0])
            return Image.fromarray(input_data)
        elif input_type == IOConverter.InputType.TORCH:
            # same as above
            if input_data.shape[0] != 1:
                print("Warning: Batch of images detected, taking first image")
            input_data = IOConverter.match_dtype(input_data[0], is_tensor=True)
            np_array = input_data.cpu().numpy()
            return Image.fromarray(np_array)
        elif input_type == IOConverter.InputType.STRING:
            return Image.open(input_data)
        elif input_type == IOConverter.InputType.GZIP_BASE64:
            decoded_data = IOConverter.read_base64(input_data)
            decompressed_data = gzip.decompress(decoded_data)
            result = Image.open(BytesIO(decompressed_data)).convert("RGB")
            return result
        elif input_type == IOConverter.InputType.BASE64:
            decoded_data = IOConverter.read_base64(input_data)
            result = Image.open(BytesIO(decoded_data)).convert("RGB")
            return result
        elif input_type == IOConverter.InputType.URL:
            response = requests.get(input_data)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        else:
            raise Exception(f"Invalid input type, {input_type}")

    @staticmethod
    def to_tensor(pil_image):
        if pil_image.mode == "I":
            pil_image = pil_image.point(lambda i: i * (1/255))  # convert to float
        np_array = np.array(pil_image).astype(np.float32) / 255.0
        tensor = torch.from_numpy(np_array)
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        # assert 4-dimensional tensor
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
    def convert_to_tensor(input_data):
        input_type = IOConverter.classify(input_data)
        if input_type == IOConverter.InputType.PIL:
            return IOConverter.to_tensor(input_data)
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
            return IOConverter.to_tensor(image)
        elif input_type == IOConverter.InputType.GZIP_BASE64:
            image = IOConverter.convert_to_pil(input_data)
            return IOConverter.to_tensor(image)
        elif input_type == IOConverter.InputType.BASE64:
            image = IOConverter.convert_to_pil(input_data)
            return IOConverter.to_tensor(image)
        elif input_type == IOConverter.InputType.URL:
            response = requests.get(input_data)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return IOConverter.to_tensor(image)
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
    def handle_input(tensor_or_image):
        pil_image = IOConverter.convert_to_pil(tensor_or_image)
        return pil_image

    @staticmethod
    def handle_output_as_pil(pil_image):
        return pil_image

    @staticmethod
    def handle_output_as_tensor(pil_image):
        return IOConverter.convert_to_tensor(pil_image)

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
