"""Threading utilities for safe inter-thread communication.

Provides a stoppable thread base class and safe queue wrappers.
"""

from __future__ import annotations

import queue
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, TypeVar

from guitarscapes.utils.logger import get_logger

logger = get_logger("utils.threading")

T = TypeVar("T")


class StoppableThread(threading.Thread):
    """Base class for threads that can be cleanly stopped.

    Subclasses must implement the `run_loop()` method, which is called
    repeatedly until `stop()` is called.
    """

    def __init__(self, name: str = "StoppableThread", daemon: bool = True) -> None:
        super().__init__(name=name, daemon=daemon)
        self._stop_event = threading.Event()
        self._error: Optional[Exception] = None

    @property
    def stopped(self) -> bool:
        """Whether the thread has been asked to stop."""
        return self._stop_event.is_set()

    @property
    def last_error(self) -> Optional[Exception]:
        """The last error that occurred in the thread, if any."""
        return self._error

    def stop(self) -> None:
        """Signal the thread to stop."""
        logger.debug("Stopping thread: %s", self.name)
        self._stop_event.set()

    def run(self) -> None:
        """Main thread entry point. Calls run_loop() until stopped."""
        logger.info("Thread started: %s", self.name)
        try:
            self.on_start()
            while not self._stop_event.is_set():
                try:
                    self.run_loop()
                except Exception as exc:
                    self._error = exc
                    logger.error(
                        "Error in thread %s: %s", self.name, exc, exc_info=True
                    )
                    if not self.on_error(exc):
                        break
        finally:
            try:
                self.on_stop()
            except Exception as exc:
                logger.error(
                    "Error during cleanup of thread %s: %s",
                    self.name,
                    exc,
                    exc_info=True,
                )
            logger.info("Thread stopped: %s", self.name)

    def on_start(self) -> None:
        """Called once when the thread starts. Override for initialization."""

    def on_stop(self) -> None:
        """Called once when the thread stops. Override for cleanup."""

    def on_error(self, error: Exception) -> bool:
        """Called when an error occurs in run_loop().

        Args:
            error: The exception that was raised.

        Returns:
            True to continue running, False to stop the thread.
        """
        return False

    def run_loop(self) -> None:
        """Main loop body. Must be implemented by subclasses."""
        raise NotImplementedError


class SafeQueue(Generic[T]):
    """Thread-safe queue wrapper with timeout and fallback support.

    Wraps `queue.Queue` with convenience methods and logging.
    """

    def __init__(self, maxsize: int = 0, name: str = "SafeQueue") -> None:
        self._queue: queue.Queue[T] = queue.Queue(maxsize=maxsize)
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def put(self, item: T, timeout: Optional[float] = None) -> bool:
        """Put an item in the queue.

        Args:
            item: The item to enqueue.
            timeout: Maximum time to wait. None for non-blocking.

        Returns:
            True if the item was enqueued, False if the queue was full.
        """
        try:
            self._queue.put(item, block=(timeout is not None), timeout=timeout)
            return True
        except queue.Full:
            logger.warning("Queue '%s' is full, dropping item.", self._name)
            return False

    def put_nowait(self, item: T) -> bool:
        """Put an item without waiting. Drops if full."""
        return self.put(item, timeout=None)

    def get(self, timeout: Optional[float] = 0.01) -> Optional[T]:
        """Get an item from the queue.

        Args:
            timeout: Maximum time to wait in seconds. None for blocking.

        Returns:
            The item, or None if the queue was empty within the timeout.
        """
        try:
            return self._queue.get(block=True, timeout=timeout)
        except queue.Empty:
            return None

    def get_nowait(self) -> Optional[T]:
        """Get an item without waiting. Returns None if empty."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def get_latest(self) -> Optional[T]:
        """Drain the queue and return only the most recent item.

        Useful when you only care about the latest state (e.g., latest chord).
        """
        latest: Optional[T] = None
        while True:
            try:
                latest = self._queue.get_nowait()
            except queue.Empty:
                break
        return latest

    def clear(self) -> int:
        """Remove all items from the queue.

        Returns:
            Number of items removed.
        """
        count = 0
        while True:
            try:
                self._queue.get_nowait()
                count += 1
            except queue.Empty:
                break
        return count

    @property
    def size(self) -> int:
        """Current number of items in the queue."""
        return self._queue.qsize()

    @property
    def empty(self) -> bool:
        """Whether the queue is empty."""
        return self._queue.empty()


@dataclass
class ThreadHealthMonitor:
    """Monitors the health of multiple threads.

    Periodically checks if registered threads are still alive and reports
    any that have died unexpectedly.
    """

    threads: dict[str, StoppableThread] = field(default_factory=dict)
    _check_interval: float = 5.0

    def register(self, thread: StoppableThread) -> None:
        """Register a thread for health monitoring."""
        self.threads[thread.name] = thread

    def unregister(self, name: str) -> None:
        """Remove a thread from monitoring."""
        self.threads.pop(name, None)

    def check_health(self) -> dict[str, bool]:
        """Check all registered threads.

        Returns:
            Dictionary mapping thread name to alive status.
        """
        status: dict[str, bool] = {}
        for name, thread in self.threads.items():
            alive = thread.is_alive()
            status[name] = alive
            if not alive and not thread.stopped:
                error = thread.last_error
                logger.error(
                    "Thread '%s' died unexpectedly. Last error: %s",
                    name,
                    error,
                )
        return status

    def all_healthy(self) -> bool:
        """Return True if all registered threads are alive."""
        return all(self.check_health().values())
