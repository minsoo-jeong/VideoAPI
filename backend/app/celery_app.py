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
    result_backend=f'redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0'
    # result_extended=True,
    # result_expires=3600,

)

celery_app.autodiscover_tasks(['app.tasks'], related_name='video_review_tasks')

__all__ = ('celery_app',)
