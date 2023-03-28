from .is_running import IsRunning
from functools import cached_property
from threading import Thread
import traceback
import sys


class HasThread(IsRunning):
    _target = None
    daemon = True
    looping = False

    @property
    def name(self):
        return self.__class__.__name__

    def _thread_target(self):
        while self.running:
            try:
                self._target()
            except Exception:
                print('Exception in thread', self.name, file=sys.stderr)
                traceback.print_exc()
                self.stop()
            else:
                if not self.looping:
                    break

    def new_thread(self, run_loop=False):
        return Thread(target=self._thread_target, daemon=self.daemon)

    @cached_property
    def thread(self):
        return self.new_thread()

    def start(self):
        return super().start() or self.thread.start()
