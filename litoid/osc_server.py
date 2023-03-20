from . thread_queue import ThreadQueue
from functools import cached_method
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from queue import Queue
from threading import Thread
from typing import Callable
import datacls


@datacls
class Server(ThreadQueue):
    callback: Callable
    endpoints: tuple[str]
    ip: str = '127.0.0.1'
    port: int = 5005
    maxsize: int = 0
    thread_count: int = 1

    def serve(self):
        self.start()
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
        self.put(address, *osc_args)
