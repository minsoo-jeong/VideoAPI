from pathlib import Path

import yaml
import json

from ultralytics import YOLO

from PIL import Image

from app.settings import settings

import importlib.util
import numpy as np
import math

yolo_cfg = importlib.util.find_spec('ultralytics.cfg')


class SeatbeltClient(object):
    MODEL_NAME = "yolo_onnx"
    INPUT_NAME = "images"
    OUTPUT_NAME = "output0"
    MODEL_VERSION = "1"
    MAX_BATCH_SIZE = 32

    coco_data = Path(yolo_cfg.origin).parent.joinpath('datasets', 'coco.yaml')

    def __init__(self):
        self.client = YOLO(f"grpc://{settings.TRITON_HOST}:{settings.TRITON_PORT}/{self.MODEL_NAME}",
                           task='detect',
                           )

    def preprocess(self, frame):
        frame = Image.fromarray(frame)
        # if frame is not rgb convert it to rgb
        assert frame.mode == 'RGB', ValueError('frame mode is not RGB')

        return frame

    def run(self, frames):
        indices = np.arange(len(frames))
        batch_indices = np.array_split(indices, math.ceil(len(indices) / self.MAX_BATCH_SIZE))
        results = []
        for idx in batch_indices:
            batch_array = [self.preprocess(f) for f in frames[idx]]

            predicts = self.client.predict(source=batch_array,
                                           conf=0.5,
                                           iou=0.45,
                                           classes=[0, 1, 3],
                                           verbose=False,
                                           data=self.coco_data,
                                           )

            results.extend([json.loads(p.tojson()) for p in predicts])

        return results
