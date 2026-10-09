"""Non-UI execution boundary for the existing HN BlackBox crypto engines."""
from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class CryptoJob:
    algorithm: str
    operation: str
    text: str
    values: dict[str, str]


class CryptoWorker:
    """Reusable executor owned by the desktop UI layer."""

    def __init__(self, max_workers: int = 2) -> None:
        self._executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="hn-crypto-worker")
        self._closed = False

    def submit(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        if self._closed:
            raise RuntimeError("CryptoWorker is shut down")
        return self._executor.submit(fn, *args, **kwargs)

    def shutdown(self, wait: bool = True) -> None:
        if not self._closed:
            self._closed = True
            self._executor.shutdown(wait=wait, cancel_futures=True)

    def __enter__(self) -> "CryptoWorker":
        return self

    def __exit__(self, *_: object) -> None:
        self.shutdown(wait=True)
