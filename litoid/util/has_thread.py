from functools import cached_property
from threading import Thread


class HasThread:
    _target = None
    daemon = True

    def new_thread(self):
        return Thread(target=self._target, daemon=self.daemon)

    @cached_property
    def thread(self):
        return self.new_thread()

    def start(self):
        self.thread.start()
