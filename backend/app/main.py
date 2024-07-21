from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import redis

from endpoints import router
from settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=0)

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
