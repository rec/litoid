from .is_running import IsRunning
from functools import cached_property
from threading import Thread
import traceback
import sys


class HasThread(IsRunning):
    _target = None
    daemon = True
    looping = False

    def _thread_target(self):
        while self.running:
            try:
                self._target()
            except Exception:
                print('Exception in', __class__, file=sys.stderr)
                traceback.print_exc()
                raise
            if not self.looping:
                self.stop()

    def new_thread(self, run_loop=False):
        return Thread(target=self._thread_target, daemon=self.daemon)

    @cached_property
    def thread(self):
        return self.new_thread()

    def start(self):
        return super().start() or self.thread.start()
