import albumentations as A
from albumentations.pytorch import ToTensorV2
import numpy as np
import torch
import h5py

import decord
import math
from PIL import Image

import tritonclient.grpc as grpcclient

import json

from app.settings import settings
from app.utils import sec2str

import importlib.util
from pathlib import Path
from collections import deque


class SBDClient(object):
    model_name = "transnetv2"
    model_version = "1"
    input_name = 'input'
    output_name = 'output0'
    seq_length = 100
    buf_length = 25
    stride = seq_length // 2

    def __init__(self):
        self.client = grpcclient.InferenceServerClient(url=f'{settings.TRITON_HOST}:{settings.TRITON_PORT}')

    def run(self, path):
        video = decord.VideoReader(path, width=48 * 2, height=27 * 2)

        preds = []
        for sequence in self.sequence_generator(video):
            preds.append(self.predict(sequence))

        preds = np.concatenate(preds)[:len(video)]
        scenes = self.predictions_to_scenes(preds).tolist()
        return scenes

    def predict(self, sequence):
        # sequence: [1,100,27,48,3]
        inputs = []
        inputs.append(grpcclient.InferInput(self.input_name, sequence.shape, "UINT8"))
        inputs[0].set_data_from_numpy(sequence)

        response = self.client.infer(self.model_name,
                                     inputs=inputs,
                                     outputs=[grpcclient.InferRequestedOutput(self.output_name)],
                                     model_version=self.model_version)

        result = response.as_numpy(self.output_name)[0, self.buf_length:-self.buf_length, 0]

        return result

    def predictions_to_scenes(self, predictions: np.ndarray, threshold: float = 0.5):
        predictions = (predictions > threshold).astype(np.uint8)

        scenes = []
        t, t_prev, start = -1, 0, 0
        for i, t in enumerate(predictions):
            if t_prev == 1 and t == 0:
                start = i
            if t_prev == 0 and t == 1 and i != 0:
                scenes.append([start, i])
            t_prev = t
        if t == 0:
            scenes.append([start, i])

        # just fix if all predictions are 1
        if len(scenes) == 0:
            return np.array([[0, len(predictions) - 1]], dtype=np.int32)

        return np.array(scenes, dtype=np.int32)

    def sequence_generator(self, video: decord.VideoReader):

        q = deque(maxlen=self.seq_length)

        for idx, frame in enumerate(video):
            frame = self.read_frame(frame)
            q.append(frame)
            if idx == 0:
                q.extend([frame] * self.buf_length)

            if idx == len(video) - 1:
                remain = q.maxlen - len(q)
                q.extend([frame] * remain)
                if remain < self.buf_length:
                    yield np.array(q)[np.newaxis]
                    q = deque(list(q)[self.stride:], maxlen=self.seq_length)
                    q.extend([frame] * (q.maxlen - len(q)))

            if len(q) == q.maxlen:
                yield np.array(q)[np.newaxis]
                q = deque(list(q)[self.stride:], maxlen=self.seq_length)

    def read_frame(self, frame):
        frame = Image.fromarray(frame.asnumpy())
        if frame.mode != 'RGB':
            raise ValueError('frame mode is not RGB')

        frame = np.array(frame.resize((48, 27)))
        return frame
