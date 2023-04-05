from typing import Callable
import datacls
import heapq
import time
from . thread_queue import HasThread

MAX_WAIT = 0.01


@datacls(slots=True)
class Event:
    timestamp: float
    action: Callable = datacls.field(compare=False)


@datacls.mutable
class TimedHeap(HasThread):
    _heap: list = datacls.field(list)
    _time: Callable = time.time
    _sleep: Callable = time.sleep

    def clear(self):
        with self.lock:
            self._heap.clear()

    def push(self, timestamp, action):
        with self._lock:
            heapq.heappush(self._head, Event(timestamp, action))

    def pop(self, timestamp=None):
        with self._lock:
            def top():
                return self._heap[0].timestamp if self._heap else None

            timestamp = timestamp or self._time()
            results = []
            while (ts := top()) and ts <= timestamp:
                results.append(heapq.heappop(self._heap))

            return results, ts

    def _target(self):
        while True:
            actions, ts = self.pop()
            [a.action() for a in actions]

            if t := not actions and (ts - self._time() if ts else MAX_WAIT):
                self._sleep(min(t, MAX_WAIT))
