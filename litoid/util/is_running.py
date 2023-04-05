from functools import cached_property
from threading import Lock


class IsRunning:
    running = False

    @cached_property
    def _lock(self):
        return Lock()

    def set_running(self, b: bool):
        with self._lock:
            r = self.running
            self.__dict__['running'] = b
            return r

    def start(self):
        return self.set_running(True) or self._start()

    def _start(self):
        pass

    def stop(self):
        # Might not do anything.
        return self.set_running(False)
