import traceback

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi import BackgroundTasks, UploadFile
from fastapi.responses import HTMLResponse
from collections import defaultdict

from functools import partial
from redis import Redis
import pickle as pk
import decord

from utils import sec2str, generate_key
from tasks.video_review import Review

from app.tasks.video_review_tasks import video_review

router = APIRouter()

TEST_VIDEO_PATH = '/mldisk/nfs_shared_/ms/enm-data/soucreData/짧은 영상/한국/HOME ep6 no smoking 단편영화 홈 6번째 에피소드_1080p.mp4'


# TEST_VIDEO_PATH = '/mldisk/nfs_shared_/ms/enm-data/soucreData/20240703/한국/삼식이 삼촌 01화 1080p.KORSUB.WEBRip.H264.AAC.mp4'


@router.post("/dummy")
def dummy(request: Request, path: str, background_tasks: BackgroundTasks):
    try:
        redis_client = request.app.state.redis  # type: Redis
        path = TEST_VIDEO_PATH
        request_id = generate_key()

        redis_client.set(request_id, pk.dumps({"status": "processing"}))

        review = Review()

        background_tasks.add_task(review.run, path,
                                  None,
                                  callback=lambda x: redis_client.set(request_id,
                                                                      pk.dumps({"status": "Done",
                                                                                "results": x})))

        return {'request_id': request_id}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dummy/{request_id}")
def dummy_result(request: Request, request_id: str):
    try:
        redis_client = request.app.state.redis  # type: Redis

        results = redis_client.get(request_id)
        if results is None:
            return {"request_id": request_id, "status": "Error", "message": "Wrong request id"}

        results = pk.loads(results)
        return {"request_id": request_id, **results}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dummy-celery")
def dummy_celery(request: Request, path: str, ):
    try:
        redis_client = request.app.state.redis  # type: Redis
        path = TEST_VIDEO_PATH

        result = video_review.delay(path)
        redis_client.set(result.id, pk.dumps({"request_id": result.id, "status": "processing"}))

        return {'request_id': result.id}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


import json


@router.get("/dummy-celery/{request_id}")
def dummy_celery_result(request: Request, request_id: str):
    try:
        redis_client = request.app.state.redis  # type: Redis

        # celery_results_key = f"celery-task-meta-{request_id}"
        results = redis_client.get(request_id)
        if results is None:
            return {"request_id": request_id, "status": "Error", "message": "Wrong request id"}
        print(results)

        results = json.loads(results)
        print(results)
        # results = pk.loads(results)
        return {"request_id": request_id, **results}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
