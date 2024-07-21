import traceback
from collections import defaultdict
import time
import json

from redis import Redis
import numpy as np
import decord

from app.utils import sec2str, print_func, elapsed
from app.clients.helmet import HelmetClient
from app.clients.seatbelt import SeatbeltClient
from app.clients.shot_boundary import SBDClient

import asyncio

from collections import defaultdict
import itertools


class Review:
    def __init__(self):
        self.helmet_client = HelmetClient()
        self.seatbelt_client = SeatbeltClient()
        self.sbd_client = SBDClient()

    def run(self, video_path, shot_path=None, callback=None):
        try:
            print(video_path)
            video = decord.VideoReader(video_path, num_threads=0, ctx=decord.cpu(0))
            shots = self.detect_shot_boundaries(video_path) if shot_path is None else np.load(shot_path)

            # shots = [[0, len(video) // 8],
            #          [len(video) // 8 + 1, 2 * len(video) // 8], ]

            results = defaultdict(list)
            for idx, (start, end) in enumerate(shots):
                _results = self.detect_helmets(video, start, end)
                results['helmet'].append(dict(shot_idx=idx,
                                              shot_start=int(start),
                                              shot_end=int(end),
                                              results=_results))

                _results = self.detect_seatbelts(video, start, end)
                results['seatbelt'].append(dict(shot_idx=idx,
                                                shot_start=int(start),
                                                shot_end=int(end),
                                                results=_results))

                # print(idx, results)

            results = dict(results)
            if callback:
                callback(results)
            else:
                return results


        except Exception as e:
            traceback.print_exc()
            raise e

    @print_func
    def detect_shot_boundaries(self, video_path):

        shots = self.sbd_client.run(video_path)

        return shots

    @print_func
    def detect_helmets(self, video, start, end):
        frame_indices = np.arange(start, end + 1, video.get_avg_fps()).astype(int).tolist()
        frames = video.get_batch(frame_indices).asnumpy()

        predicts = self.helmet_client.run(frames)

        results = []
        for idx, pred in zip(frame_indices, predicts):
            if len(pred):
                results.append(dict(frame_idx=idx,
                                    timestamp=sec2str(idx / video.get_avg_fps()),
                                    result=pred))

        return results

    @print_func
    def detect_seatbelts(self, video, start, end):
        frame_indices = np.arange(start, end + 1, video.get_avg_fps() * 2).astype(int).tolist()
        frames = video.get_batch(frame_indices).asnumpy()

        predicts = self.seatbelt_client.run(frames)

        results = []
        for idx, pred in zip(frame_indices, predicts):
            if len(pred):
                results.append(dict(frame_idx=idx,
                                    timestamp=sec2str(idx / video.get_avg_fps()),
                                    result=pred))

        return results
