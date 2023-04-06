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
            except Exception as e:
                print('Exception', self, self.name, e, file=sys.stderr)
                traceback.print_stack()
                self.stop()
                raise
            else:
                if not self.looping:
                    break

    def new_thread(self, run_loop=False):
        return Thread(target=self._thread_target, daemon=self.daemon)

    @cached_property
    def thread(self):
        return self.new_thread()

    def _start(self):
        self.thread.start()
