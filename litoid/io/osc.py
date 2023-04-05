from ..util.thread_queue import ThreadQueue
from functools import cached_property
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer
from typing import Callable
import datacls


@datacls.mutable
class Desc:
    endpoints: tuple[str] = ()
    ip: str = '127.0.0.1'
    port: int = 5005
    maxsize: int = 0
    thread_count: int = 1

    def server(self):
        return BlockingOSCUDPServer(self.ip, self.port, self.dispatcher)


class Message(tuple):
    pass


@datacls.mutable
class Server(Desc, ThreadQueue):
    callback: Callable = print

    def serve(self):
        self.start()
        self.desc.server().serve_forever()

    @cached_property
    def dispatcher(self):
        d = Dispatcher()
        for e in self.endpoints:
            d.map(f'/{e}', self.osc_callback)
        return d

    def osc_callback(self, address, *osc_args):
        self.put(Message(address, *osc_args))
