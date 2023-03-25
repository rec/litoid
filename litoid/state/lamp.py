from . import instruments
from ..io.dmx import DMX
from .instrument import Instrument
from functools import cached_property
import datacls


@datacls
class LampDesc:
    instrument: str
    offset: int

    def make(self, dmx: DMX):
        instrument = instruments()[self.intrument]
        size = len(instrument.channels)
        frame = dmx.dmx_frame[self.offset:self.offset + size]
        return Lamp(frame=frame, instrument=instrument, offset=self.offset)


@datacls
class Lamp:
    frame: memoryview
    instrument: Instrument
    offset: int

    @cached_property
    def presets(self):
        return self.instrument.mapped_presets

    @cached_property
    def label(self):
        return f'{self.instrument.name}_{self.offset}'

    def render(self, d: dict):
        it = range(len(self.frame))
        self.frame[:] = (max(0, min(255, d.get(i, 0))) for i in it)


def lamps(dmx: DMX, descs: list):
    lamps = [LampDesc(**d).make(dmx) for d in descs]

    assert len(set(la.label for la in lamps)) == len(lamps)
    lamps = {la.label: la for la in lamps}

    # Check for overlapping lamps
    entries = {}
    for p in lamps.values():
        for i in range(len(p.frame)):
            entries.setdefault(p.offset + i, []).append((p, i))

    if bad := {k: v for k, v in entries.items() if len(v) > 1}:
        raise ValueError(str(bad))

    return lamps
