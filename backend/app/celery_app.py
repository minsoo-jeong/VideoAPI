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

from app.tasks.video_review import Review

from celery import shared_task
from celery import Celery

from app.settings import settings

celery_app = Celery(
    'video_api',
    broker=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0',  # Redis를 브로커로 사용
    backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0'
)

celery_app.conf.update(
    accept_content=["json", "pickle"],
    task_serializer="pickle",
    result_serializer="json",
    # result_extended=True,
    # result_expires=3600,
)

celery_app.autodiscover_tasks(['app.tasks'], related_name='video_review_tasks')


__all__ = ('celery_app',)
