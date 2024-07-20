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