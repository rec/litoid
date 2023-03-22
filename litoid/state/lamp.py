from ..io.dmx import DMX
from .instrument import Instrument
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

    @cached_property
    def label(self):
        return f'{self.name}_{self.offset}'


@datacls
class Lamp(LampDesc):
    frame: np.ndarray = datacls.field(np.array)

    def render(self, d: dict):
        it = range(len(self.frame))
        self.frame[:] = (max(0, min(255, d.get(i, 0))) for i in it)


class Lamps:
    def __init__(self, dmx: DMX, descs: list[LampDesc, ...]):
        self.lamps = tuple(d.make(dmx) for d in descs)
        entries = {}
        for p in self.lamps:
            for i in range(len(p.frame)):
                entries.setdefault(p.offset + i, []).append((p, i))
        if bad := {k: v for k, v in entries.items() if len(v) > 1}:
            raise ValueError(str(bad))
