from . import instruments
from ..io.dmx import DMX
from functools import cached_property
import datacls


@datacls.mutable
class LampDesc:
    name: str
    iname: str
    offset: int

    @cached_property
    def instrument(self):
        return instruments()[self.iname]

    @cached_property
    def size(self):
        return len(self.instrument.channels)

    def make(self, dmx: DMX):
        frame = dmx.frame[self.offset:self.offset + self.size]
        return Lamp(frame=frame, dmx=dmx, **self.asdict())

    @cached_property
    def channel_range(self):
        return range(self.offset, self.offset + self.size)


@datacls.mutable
class Lamp(LampDesc):
    frame: memoryview
    dmx: DMX

    def set_levels(self, d: dict):
        d = self.instrument.remap_dict(d)
        it = range(len(self.frame))
        self.frame[:] = (bytes(max(0, min(255, d.get(i, 0))) for i in it))
        self.send_packet()

    def set_level(self, i: int | slice, v):
        if isinstance(i, slice):
            v = bytes(max(0, min(255, i)) for i in v)
        else:
            v = max(0, min(255, v))
        self.frame[i] = v

    def blackout(self):
        self.set_levels(self.instrument.blackout)

    def send_packet(self):
        self.dmx.send_packet()


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
