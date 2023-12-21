import base64
import sys
import os
import io

import cv2
import numpy as np
import typing

from PIL import Image
from mltu.configs import BaseModelConfigs
from mltu.inferenceModel import OnnxInferenceModel

from mltu.utils.text_utils import ctc_decoder, get_cer

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), './../..')))

from . import CONST


class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, bytes_image):
        image = Image.open(io.BytesIO(bytes_image))
        image_np_array = np.array(image)
        image = cv2.resize(image_np_array, self.input_shape[:2][::-1])
        image_pred = np.expand_dims(image, axis=0).astype(np.float32)
        preds = self.model.run(None, {self.input_name: image_pred})[0]
        text = ctc_decoder(preds, self.char_list)[0]
        return text


class ImageCaptchaSolver:
    def __init__(self):
        self.char_list = "CcVltR3Ns2IB8vekm9XuwbdjAiPUGzYfSLgyDKEQqao1n5TFxOhHW4pM06J7Zr"
        self.input_shape = [50, 200, 3]
        model_path = "./cnn/image_model/models/202311272055"
        configs_path = os.path.join(model_path, 'configs.yaml')

        configs = BaseModelConfigs.load(configs_path)
        configs.model_path = model_path.replace('\\', '/')

        self.model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    def solve(self, b64_image):
        print('Converting b64 to bytes...')
        bytes_image = self.convert_b64_to_bytes(b64_image)

        print('Extracting text from image...')
        text = self.model.predict(bytes_image)

        return text

    def convert_b64_to_bytes(self, b64_image):
        return base64.b64decode(b64_image)
