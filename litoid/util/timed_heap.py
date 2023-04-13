from typing import Callable
import datacls
import heapq
import time
from . thread_queue import HasThread

MAX_WAIT = 0.01


@datacls.mutable
class TimedHeap(HasThread):
    heap: list = datacls.field(list)
    _time: Callable = time.time
    _sleep: Callable = time.sleep
    looping = True

    def clear(self):
        with self.lock:
            self.heap.clear()

    def __post_init__(self):
        heapq.heapify(self.heap)

    def push(self, action):
        with self._lock:
            heapq.heappush(self._head, action)

    def pop(self, timestamp=None):
        with self._lock:
            def top():
                return self.heap[0].timestamp if self.heap else None

            timestamp = timestamp or self._time()
            results = []
            while (ts := top()) and ts <= timestamp:
                results.append(heapq.heappop(self.heap))

            return results, ts

    def _target(self):
        actions, ts = self.pop()
        for a in actions:
            a()

        if not actions:
            if t := ts - self._time() if ts else MAX_WAIT:
                self._sleep(min(t, MAX_WAIT))
