import datacls
import heapq
import time
from . thread_queue import HasThread

MAX_WAIT = 0.01


@datacls.mutable
class TimedHeap(HasThread):
    heap: list = datacls.field(list)
    looping = True

    def clear(self):
        with self.lock:
            self.heap.clear()

    def __post_init__(self):
        heapq.heapify(self.heap)

    def push(self, event):
        with self._lock:
            heapq.heappush(self._head, event)

    def pop(self, timestamp=None):
        with self._lock:
            def top():
                return self.heap[0].timestamp if self.heap else None

            timestamp = timestamp or time.time()
            results = []
            while (next_ts := top()) and next_ts <= timestamp:
                results.append(heapq.heappop(self.heap))

            return results, next_ts

    def _target(self):
        events, next_ts = self.pop()
        for e in events:
            e()

        if not next_ts:
            time.sleep(MAX_WAIT)
        elif (ts := (next_ts - time.time())) > 0:
            time.sleep(min(ts, MAX_WAIT))
