from . import instruments
from ..io.dmx import DMX
from functools import cached_property
import datacls


@datacls.mutable
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
        return Lamp(frame=frame, dmx=dmx, **self.asdict())


@datacls.mutable
class Lamp(LampDesc):
    frame: memoryview
    dmx: DMX

    @property
    def iname(self) -> str:
        return self.instrument.name

    @property
    def levels(self) -> dict:
        return self.instrument.unmap_frame(self.frame)

    @levels.setter
    def levels(self, d: dict):
        d = self.instrument.remap_dict(d)
        it = range(len(self.frame))
        self[:] = bytes(max(0, min(255, d.get(i, 0))) for i in it)
        self.send_packet()

    def __len__(self):
        return len(self.frame)

    def __getitem__(self, i):
        return self.frame[i]

    def __setitem__(self, i, v):
        if isinstance(i, slice):
            v = bytes(max(0, min(255, i)) for i in v)
        else:
            i, v = self.instrument.remap(i, v)
            v = max(0, min(255, v))
        self.frame[i] = v

    def blackout(self):
        self.levels = self.instrument.blackout

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
