"""asyncio helpers that also work on Windows.

psycopg cannot run in async mode on Windows' default event loop (ProactorEventLoop),
so every entry point that starts a loop (worker, Alembic, tests) goes through here.
"""

import asyncio
import sys
from collections.abc import Coroutine
from typing import Any


def new_event_loop() -> asyncio.AbstractEventLoop:
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop()
    return asyncio.new_event_loop()


def run[T](coro: Coroutine[Any, Any, T]) -> T:
    return asyncio.run(coro, loop_factory=new_event_loop)
