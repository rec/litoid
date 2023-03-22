from . dmx import DMX
from . instrument import Instrument
from functools import cached_property
import datacls
import numpy as np


@datacls
class LampDesc:
    instrument: Instrument
    name: str
    offset: int = 0

    def make(self, dmx: DMX):
        size = len(self.instrument.channels)
        frame = dmx.dmx_frame[self.offset:self.offset + size]
        return Lamp(frame=frame, **self.asdict())

    @cached_property
    def presets(self):
        return self.instrument.mapped_presets


@datacls
class Lamp(LampDesc):
    frame: np.darray

    def render(self, d: dict):
        it = range(len(self.frame))
        self.frame[:] = (max(0, min(255, d.get(i, 0))) for i in it)
