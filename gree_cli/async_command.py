import asyncio
from functools import wraps

from .app import app


def asyncio_run(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    return wrapper


@wraps(app.command)
def async_command(*args, **kwargs):
    def decorator(func):
        return app.command(*args, **kwargs)(asyncio_run(func))

    return decorator
