from functools import cached_property
from queue import Queue
import threading


class HasThread:
    _target = None
    daemon = True

    def new_thread(self):
        return threading.Thread(target=self._target, daemon=self.daemon)

    @cached_property
    def thread(self):
        return self.new_thread()

    def start(self):
        self.thread.start()


class ThreadQueue(HasThread):
    maxsize = 1
    thread_count = 1
    callback = print
    thread = None

    def start(self):
        [t.start() for t in self.threads]

    @cached_property
    def queue(self):
        return Queue(self.maxsize)

    def put(self, item):
        self.queue.put_nowait(item)

    @cached_property
    def threads(self):
        return tuple(self.new_thread() for i in range(self.thread_count))

    def _target(self):
        while (item := self.queue.get()) is not None:
            self.callback(item)
