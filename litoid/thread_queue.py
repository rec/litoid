from functools import cached_method
from queue import Queue
from threading import Thread


class ThreadQueue:
    maxsize = 1
    thread_count = 1
    daemon = True
    callback = None

    def start(self):
        [t.start() for t in self.threads]

    @cached_method
    def queue(self):
        return Queue(self.maxsize)

    def put(self, *args):
        self.queue.put_nowait(args)

    @cached_method
    def threads(self):
        return tuple(self._thread() for i in range(self.thread_count))

    def _thread(self):
        return Thread(target=self._target, daemon=self.daemon)

    def _target(self):
        while (d := self.queue.get()) is not None:
            self.callback(*d)
