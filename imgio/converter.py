from PIL import Image
import numpy as np
import base64
import torch
import requests
import os
from io import BytesIO

class IOConverter:
    """
    Classify the input data type.
    
    Assumes the inputs to be following:

    - PIL Image
    - numpy array
    - torch tensor
    - string (path to image)
    - base64 string (which can be decoded to bytes and then to image)
    - URL (which can be downloaded to image)
    
    do NOT pass unsafe URLs / base64 strings, as it may cause security issues.
    """

    class InputType:
        PIL = "PIL"
        NUMPY = "NUMPY"
        TORCH = "TORCH"
        STRING = "STRING"
        BASE64 = "BASE64"
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
                raise Exception(f"Invalid string input, {input_data:10}")
        else:
            raise Exception(f"Invalid input type, {type(input_data)}")
    
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
            input_data = input_data[0] * 255.0
            input_data = input_data.astype('uint8')
            return Image.fromarray(input_data)
        elif input_type == IOConverter.InputType.TORCH:
            # same as above
            if input_data.shape[0] != 1:
                print("Warning: Batch of images detected, taking first image")
            input_data = input_data[0].cpu().numpy() * 255.0
            input_data = input_data.astype('uint8')
            return Image.fromarray(input_data)
        elif input_type == IOConverter.InputType.STRING:
            return Image.open(input_data)
        elif input_type == IOConverter.InputType.BASE64:
            return Image.open(BytesIO(base64.b64decode(input_data)))
        elif input_type == IOConverter.InputType.URL:
            response = requests.get(input_data)
            return Image.open(BytesIO(response.content))
        else:
            raise Exception(f"Invalid input type, {input_type}")
    @staticmethod
    def to_tensor(pil_image):
        if pil_image.mode == "I":
            pil_image = pil_image.point(lambda i: i * (1/255)) # convert to float
        np_array = np.array(pil_image).astype(np.float32) / 255.0
        image = torch.from_numpy(np_array)[None,][0]
        image = image[None,] # to batch
        return image
    @staticmethod
    def convert_to_tensor(input_data):
        input_type = IOConverter.classify(input_data)
        if input_type == IOConverter.InputType.PIL:
            return IOConverter.to_tensor(input_data)
        elif input_type == IOConverter.InputType.NUMPY:
            return torch.from_numpy(input_data)
        elif input_type == IOConverter.InputType.TORCH:
            return input_data
        elif input_type == IOConverter.InputType.STRING:
            image = Image.open(input_data)
            return IOConverter.to_tensor(image)
        elif input_type == IOConverter.InputType.BASE64:
            image = Image.open(BytesIO(base64.b64decode(input_data)))
            return IOConverter.to_tensor(image)
        elif input_type == IOConverter.InputType.URL:
            response = requests.get(input_data)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return IOConverter.to_tensor(image)
        else:
            raise Exception(f"Invalid input type, {input_type}")
    
    @staticmethod
    def convert_to_base64(input_data):
        input_type = IOConverter.classify(input_data)
        if input_type == IOConverter.InputType.PIL:
            buffered = BytesIO()
            input_data.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode("utf-8")
        elif input_type == IOConverter.InputType.NUMPY:
            return IOConverter.convert_to_base64(Image.fromarray(input_data))
        elif input_type == IOConverter.InputType.TORCH:
            return IOConverter.convert_to_base64(Image.fromarray(input_data.cpu().numpy()))
        elif input_type == IOConverter.InputType.STRING:
            return IOConverter.convert_to_base64(Image.open(input_data))
        elif input_type == IOConverter.InputType.BASE64:
            return input_data
        elif input_type == IOConverter.InputType.URL:
            response = requests.get(input_data)
            return base64.b64encode(response.content).decode("utf-8")
        else:
            raise Exception(f"Invalid input type, {input_type}")

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

