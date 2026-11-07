"""Small process-local cache for the public menu.

The Docker backend uses one worker. The short TTL also bounds stale reads if a
second process or a maintenance script changes the database directly.
"""

from collections import OrderedDict
from threading import RLock
from time import monotonic
from typing import Callable, Hashable, TypeVar


T = TypeVar("T")


class MenuCache:
    def __init__(self, ttl_seconds: int = 30, max_entries: int = 128):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries: OrderedDict[Hashable, tuple[float, tuple]] = OrderedDict()
        self._lock = RLock()

    def get_or_load(self, key: Hashable, loader: Callable[[], list[T]]) -> tuple[tuple[T, ...], bool]:
        with self._lock:
            now = monotonic()
            cached = self._entries.get(key)
            if cached is not None and now < cached[0]:
                self._entries.move_to_end(key)
                return cached[1], True

            value = tuple(loader())
            self._entries[key] = (monotonic() + self.ttl_seconds, value)
            self._entries.move_to_end(key)
            if len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)
            return value, False

    def invalidate(self) -> None:
        with self._lock:
            self._entries.clear()


menu_cache = MenuCache()
