from functools import cached_property
from threading import Thread
import traceback
import sys


class HasThread:
    _target = None
    daemon = True

    def new_thread(self):
        def target():
            try:
                self._target()
            except Exception:
                print('Exception in', __class__, file=sys.stderr)
                traceback.print_exc()
                raise

        return Thread(target=target, daemon=self.daemon)

    @cached_property
    def thread(self):
        return self.new_thread()

    def start(self):
        self.thread.start()
