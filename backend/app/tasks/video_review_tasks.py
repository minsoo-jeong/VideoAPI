from collections import defaultdict
import traceback
import time
import json

from celery.result import EagerResult, AsyncResult
from celery import shared_task, group, chord
import celery
from redis import Redis
import numpy as np
import decord

from app.utils import sec2str, print_func, elapsed
from app.celery_app import celery_app
from app.settings import settings
from app.clients.shot_boundary import SBDClient
from app.clients.seatbelt import SeatbeltClient
from app.clients.helmet import HelmetClient

# initialized when the worker is started
sbd_client = SBDClient()
helmet_client = HelmetClient()
seatbelt_client = SeatbeltClient()


@celery_app.task(bind=True, max_retries=0)
def video_review(self, video_path):
    try:
        print(self)

        shots = detect_shot_boundaries_task.apply((video_path,))  # type: celery.result.EagerResult
        if shots.failed():
            raise Exception()

        shot_tasks = []
        for idx, (start, end) in enumerate(shots.result['result']):
            # analyze shot

            shot_tasks.append(detect_helmets_task.s(video_path, start, end))
            shot_tasks.append(detect_seatbelts_task.s(video_path, start, end))

        jobs = chord(shot_tasks)(gather_results.s(key=self.request.id, data=dict(shot=shots.result['result'])))
        print(jobs)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task
def gather_results(results, key, data: dict = None):
    if data is None:
        data = dict()

    client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    _results = defaultdict(list)
    for result in results:
        task_type = result['task']
        _results[task_type].extend(result['result'])

    data.update(_results)

    client.set(key, json.dumps(data))


@celery_app.task(bind=True, max_retries=3)
def detect_shot_boundaries_task(self, video_path):
    try:
        print(f'{self} {self.request.id} {video_path}')
        shots = sbd_client.run(video_path)

        return dict(task='shot_boundary', result=shots)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True, max_retries=3)
def detect_helmets_task(self, video_path, start, end):
    try:
        print(f'{self} {self.request.id} {video_path} {start} {end}')
        video = decord.VideoReader(video_path, num_threads=0, ctx=decord.cpu(0))
        frame_indices = np.arange(start, end + 1, video.get_avg_fps()).astype(int).tolist()
        frames = video.get_batch(frame_indices).asnumpy()

        predicts = helmet_client.run(frames)

        results = []
        for idx, pred in zip(frame_indices, predicts):
            if len(pred):
                results.append(dict(frame_idx=int(idx),
                                    timestamp=sec2str(idx / video.get_avg_fps()),
                                    result=pred))

        # results = convert_to_native_types(results)
        return dict(task='helmet', result=results)
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task(bind=True)
def detect_seatbelts_task(self, video_path, start, end):
    try:
        print(f'{self} {self.request.id} {video_path} {start} {end}')
        video = decord.VideoReader(video_path, num_threads=0, ctx=decord.cpu(0))
        frame_indices = np.arange(start, end + 1, video.get_avg_fps() * 2).astype(int).tolist()
        frames = video.get_batch(frame_indices).asnumpy()

        predicts = seatbelt_client.run(frames)

        results = []
        for idx, pred in zip(frame_indices, predicts):
            if len(pred):
                results.append(dict(frame_idx=int(idx),
                                    timestamp=sec2str(idx / video.get_avg_fps()),
                                    result=pred))

        return dict(task='seatbelts', result=results)
    except Exception as exc:
        self.retry(exc=exc)
