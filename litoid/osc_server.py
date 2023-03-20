from functools import cached_method
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from queue import Queue
from threading import Thread
from typing import Callable
import datacls


@datacls
class Server:
    callback: Callable
    endpoints: tuple[str]
    ip: str = '127.0.0.1'
    port: int = 5005
    maxsize: int = 0
    thread_count: int = 1

    def serve(self):
        [t.start() for t in self.threads]
        self.server.serve_forever()

    @cached_method
    def server(self):
        return BlockingOSCUDPServer(self.ip, self.port, self.dispatcher)

    @cached_method
    def dispatcher(self):
        d = Dispatcher()
        for e in self.endpoints:
            d.map(f'/{e}', self.osc_callback)
        return d

    def osc_callback(self, address, *osc_args):
        queue.put_nowait((address, *osc_args))

    @cached_method
    def queue(self):
        return Queue(self.maxsize)

    @cached_method
    def threads(self):
        it = range(self.thread_count)
        return tuple(Thread(target=self._target, daemon=True) for i in it)

    def _target(self):
        while (d := self.queue.get()) is not None:
            self.callback(*d)
