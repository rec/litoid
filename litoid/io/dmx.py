from ..util.thread_queue import ThreadQueue
from functools import cached_property
import datacls


@datacls
class DMX(ThreadQueue):
    port: str

    @cached_property
    def connection(self):
        import pyenttec

        return pyenttec.DMXConnection(self.port, use_numpy=True)

    @cached_property
    def frame(self):
        import numpy as np

        return np.array(self.connection.dmx_frame, copy=False)

    def put(self, function, *args):
        assert callable(function)
        super().put(function, *args)

    def render(self):
        self.connection.render()

    def callback(self, f, *args):
        f(self.frame, *args)
        self.render()
