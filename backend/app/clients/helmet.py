from pathlib import Path
import math
import yaml
import json

from ultralytics.engine.results import Results, Boxes
from ultralytics.utils import ops
from albumentations.pytorch import ToTensorV2
from PIL import Image

import tritonclient.grpc as grpcclient
import albumentations as A
import numpy as np
import torch

from app.utils import generate_key
from app.settings import settings

import importlib.util

yolo_cfg = importlib.util.find_spec('ultralytics.cfg')


class HelmetClient(object):
    MODEL_NAME = "yolo_onnx"
    INPUT_NAME = "images"
    OUTPUT_NAME = "output0"
    MODEL_VERSION = "1"
    MAX_BATCH_SIZE = 32

    coco_data = Path(yolo_cfg.origin).parent.joinpath('datasets', 'coco.yaml')
    names = yaml.safe_load(open(coco_data, 'r'))['names']

    transform = A.Compose([
        A.LongestMaxSize(640),
        A.PadIfNeeded(640, 640, border_mode=0, value=(114, 114, 114)),
        A.Normalize(mean=[0, 0, 0], std=[1, 1, 1]),
        ToTensorV2()
    ])

    def __init__(self):
        self.client = grpcclient.InferenceServerClient(url=f'{settings.TRITON_HOST}:{settings.TRITON_PORT}')

    def preprocess(self, frame):
        frame = Image.fromarray(frame)
        # if frame is not rgb convert it to rgb
        assert frame.mode == 'RGB', ValueError('frame mode is not RGB')

        tensor = self.transform(image=np.array(frame))['image']

        return tensor.numpy()

    def postprocess(self, preds, pred_shape, orig_shape):
        preds = torch.tensor(preds)
        preds = ops.non_max_suppression(preds,
                                        0.25,
                                        0.45,
                                        classes=[0, 1, 3],
                                        agnostic=False,
                                        )

        results = []
        for i, pred in enumerate(preds):
            pred[:, :4] = ops.scale_boxes(pred_shape, pred[:, :4], orig_shape)

            boxes = Boxes(pred, orig_shape).numpy()
            results.append([{'name': self.names[int(cls)],
                             'class': int(cls),
                             'confidence': float(conf),
                             'box': dict(x1=float(box[0]), y1=float(box[1]), x2=float(box[2]), y2=float(box[3]))}
                            for cls, conf, box in zip(boxes.cls, boxes.conf, boxes.xyxy)])

        return results

    def run(self, frames):
        indices = np.arange(len(frames))
        batch_indices = np.array_split(indices, math.ceil(len(indices) / self.MAX_BATCH_SIZE))

        frame_size = Image.fromarray(frames[0]).size

        results = []
        for idx in batch_indices:
            batch_array = np.array([self.preprocess(f) for f in frames[idx]])

            _input = grpcclient.InferInput(self.INPUT_NAME, batch_array.shape, "FP32")
            _input.set_data_from_numpy(batch_array)

            infer_result = self.client.infer(model_name=self.MODEL_NAME,
                                             inputs=[_input],
                                             outputs=[grpcclient.InferRequestedOutput(self.OUTPUT_NAME)],
                                             model_version=self.MODEL_VERSION
                                             )
            preds = infer_result.as_numpy(self.OUTPUT_NAME)
            batch_result = self.postprocess(preds, batch_array.shape[2:], frame_size[::-1])
            results.extend(batch_result)
        return results
