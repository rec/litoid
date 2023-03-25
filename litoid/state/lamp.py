from . import instruments
from ..io.dmx import DMX
from functools import cached_property
import datacls


@datacls
class LampDesc:
    name: str
    instrument_name: str
    offset: int

    @cached_property
    def instrument(self):
        return instruments()[self.instrument_name]

    @cached_property
    def size(self):
        return len(self.instrument.channels)

    def make(self, dmx: DMX):
        frame = dmx.frame[self.offset:self.offset + self.size]
        return Lamp(frame=frame, **self.asdict())


@datacls
class Lamp(LampDesc):
    frame: memoryview

    @cached_property
    def presets(self):
        return self.instrument.mapped_presets

    def render(self, d: dict):
        it = range(len(self.frame))
        self.frame[:] = (max(0, min(255, d.get(i, 0))) for i in it)

    def __getitem__(self, i):
        return self.frame[i]

    def __setitem__(self, i, v):
        if isinstance(i, slice):
            v = (max(0, min(255, i)) for i in v)
        else:
            v = max(0, min(255, v))
        self.frame[i] = v


def lamps(dmx: DMX, descs: dict[str, dict]):
    lamps = {k: LampDesc(k, *v).make(dmx) for k, v in descs.items()}

    # Check for overlapping lamps
    entries = {}
    for p in lamps.values():
        for i in range(len(p.frame)):
            entries.setdefault(p.offset + i, []).append((p, i))

    if bad := {k: v for k, v in entries.items() if len(v) > 1}:
        raise ValueError(str(bad))

    return lamps
