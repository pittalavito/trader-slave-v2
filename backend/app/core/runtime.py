"""Starting async entry points (API worker, engine, Alembic) the same way on every OS."""

import asyncio
import sys
from collections.abc import Coroutine
from typing import Any


def run_async[T](main: Coroutine[Any, Any, T]) -> T:
    """`asyncio.run`, with the event loop psycopg needs on Windows.

    The default Windows loop (Proactor) is not supported by psycopg in async mode,
    so on Windows we use the Selector loop instead.
    """
    if sys.platform == "win32":
        return asyncio.run(main, loop_factory=asyncio.SelectorEventLoop)
    return asyncio.run(main)
