from functools import cached_property
import datacls
import pyenttec


@datacls.mutable
class DMX:
    port: str

    @cached_property
    def connection(self):
        return pyenttec.DMXConnection(self.port)

    @cached_property
    def frame(self):
        return memoryview(self.connection.dmx_frame)

    def send_packet(self):
        self.connection.render()
