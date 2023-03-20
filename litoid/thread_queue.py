from functools import cached_method
from queue import Queue
import threading


class HasThread:
    _target = None
    daemon = True

    def new_thread(self):
        return threading.Thread(target=self._target, daemon=self.daemon)

    @cached_method
    def thread(self):
        return self.new_thread()

    def start(self):
        self.thread.start()


class ThreadQueue(HasThread):
    maxsize = 1
    thread_count = 1
    callback = None
    thread = None

    def start(self):
        [t.start() for t in self.threads]

    @cached_method
    def queue(self):
        return Queue(self.maxsize)

    def put(self, *args):
        self.queue.put_nowait(args)

    @cached_method
    def threads(self):
        return tuple(self.new_thread() for i in range(self.thread_count))

    def _target(self):
        while (d := self.queue.get()) is not None:
            self.callback(*d)
