import datetime

import uuid

from functools import wraps
import time


def current_time():
    return datetime.datetime.now().strftime('%y%m%d%H%M%S')


def sec2str(sec: float):
    dur = datetime.timedelta(seconds=sec)
    return str(dur)


def generate_key():
    # current_time()
    return str(uuid.uuid4())


def print_func(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Start {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"End {func.__name__}")
        return result

    return wrapper


def elapsed(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        print(f"{func.__name__} elapsed time: {time.perf_counter() - start}")
        return result

    return wrapper


def to_native_type(value):
    if isinstance(value, dict):
        return {k: to_native_type(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [to_native_type(item) for item in value]
    elif isinstance(value, np.ndarray):
        return value.tolist()
    elif isinstance(value, (np.int32, np.int64, np.float32, np.float64)):
        return value.item()
    elif isinstance(value, (int, float, str, bool, type(None))):
        return value
    else:
        # 추가적인 변환이 필요할 경우 여기에 작성
        return str(value)  # 기본적으로 문자열로 변환


def convert_to_native_types(data):
    if isinstance(data, dict):
        return {k: to_native_type(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [to_native_type(item) for item in data]
    else:
        raise ValueError("Input must be a dictionary or a list")
