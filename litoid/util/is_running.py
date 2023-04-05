from functools import cached_property
from threading import Lock


class IsRunning:
    running = False

    @cached_property
    def _lock(self):
        return Lock()

    def start(self):
        with self._lock:
            if self.running:
                return True
            self.running = True

        self._start()

    def _start(self):
        pass

    def stop(self):
        # Might not do anything.
        self.running = False
