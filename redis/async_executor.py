import asyncio
import threading
from concurrent import futures
from functools import wraps
from typing import Awaitable, Tuple


__event_loop = asyncio.new_event_loop()


def _func():
    asyncio.set_event_loop(__event_loop)
    __event_loop.run_forever()


# Thread locals will not be copied
# Make sure to send all required args to the coroutine call
__thread = threading.Thread(target=_func, name="looper", daemon=True)
__thread.start()


def run_async_job(cor: Awaitable) -> futures.Future:
    """Use this to run a task asynchronously."""
    return asyncio.run_coroutine_threadsafe(cor, loop=__event_loop)


def complete_async_jobs(*cors: Awaitable) -> Tuple[futures.Future, ...]:
    """Use this to optimize execution by delegating I/O tasks to async concurrency"""
    return asyncio.run_coroutine_threadsafe(
        asyncio.wait(cors, loop=__event_loop),
        loop=__event_loop,
    ).result()[0]


def async_to_sync(cor):
    """Decorator used to convert async function to sync.
    This would do exactly what cor would, raise exceptions if any, accept the same args etc.
    """

    @wraps(cor)
    def inner(*args, **kwargs):
        return run_async_job(cor(*args, **kwargs)).result()

    return inner


loop = __event_loop
__all__ = ["run_async_job", "complete_async_jobs", "async_to_sync", "loop"]
