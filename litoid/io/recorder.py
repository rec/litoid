from .track import Track
from litoid import log
from pathlib import Path
import datacls
import numpy as np
import time as _time

SEP = '-'


@datacls.mutable
class Recorder:
    """
    A Recorder record and timestamps messages which are sequences of bytes,
    like MIDI or DMX.

    The first one or more bytes are used as a key into a dict of Tracks,
    and the remaining bytes are stored in a `uint8` array, and the timestamps
    in a parallel `float64` array

    This only works for protocols where you can deduce the length of the packet
    from the initial bytes only.
    """
    name: str
    path: Path | None = None
    tracks: dict = datacls.field(dict[str, Track])
    start_time: float = datacls.field(_time.time)
    update_time: float = datacls.field(_time.time)

    def __post_init__(self):
        if self.path and self.path.exists():
            self._fill_from_dict(np.load(self.path))
            log.debug(f'Loaded {self.name}', self.report())

    def record(self, data: list, key_size: int, time: float = 0):
        time = time or _time.time()
        key = SEP.join(str(i) for i in data[:key_size])

        byte_width = len(data) - key_size
        if (track := self.tracks.get(key)) is None:
            track = Track(byte_width)
            self.tracks[key] = track
        else:
            assert track.byte_width == byte_width

        track.append(data[key_size:], time)
        self.update_time = time

        if empty := sorted(k for k, v in self.tracks.items() if not v.empty):
            log.error('Empty tracks', *empty)

    def save(self):
        if self.path:
            np.savez(self.path, **self.asdict())
            log.debug(f'Saved {self.name}', self.report())

    def report(self):
        return {
            'event_count': {k: t.count for k, t in self.tracks.items()},
            'total_event_count': sum(t.count for t in self.tracks.values()),
            'track_count': len(self.tracks),
        }

    def plottable(self):
        return [i for t in self.tracks.values() for i in t.astuple()]

    def asdict(self):
        data = {'times': np.array((self.start_time, self.update_time))}

        for key, track in sorted(self.tracks.items()):
            for name, array in track.asdict().items():
                if len(array):
                    joined_key = SEP.join((key, name))
                    data[joined_key] = array

        return data

    @classmethod
    def fromdict(cls, d):
        c = cls()
        c._fill_from_dict(d)
        return c

    def _fill_from_dict(self, d):
        parts = {}
        for joined_key, array in d.items():
            if joined_key == 'times':
                self.start_time, self.update_time = array
            else:
                key, _, name = joined_key.rpartition(SEP)
                parts.setdefault(key, {})[name] = array

        self.tracks = {k: Track.fromdict(**v) for k, v in parts.items()}
