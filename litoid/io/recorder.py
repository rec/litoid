from .track import Track
import datacls
from litoid import log
import numpy as np
import time as _time

SEP = '-'


@datacls.mutable
class Recorder:
    """
    A Recorder record and timestamps messages which are sequences of bytes,
    like MIDI or DMX.

    The first one or more bytes are used as a key into a dict of Tracks,
    and the remaining bytes are stored in a numpy array, as are the timestamps.

    This only works for protocols where you can deduce the length of the
    packet from the initial bytes.
    """
    tracks: dict = datacls.field(dict[tuple, Track])
    start_time: float = datacls.field(_time.time)
    update_time: float = datacls.field(_time.time)

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

    def report(self):
        return {
            'event_count': {k: t.count for k, t in self.tracks.items()},
            'total_event_count': sum(t.count for t in self.tracks.values()),
            'track_count': len(self.tracks),
        }

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
        parts = {}
        for joined_key, array in d.items():
            if joined_key == 'times':
                start_time, update_time = array
            else:
                key, _, name = joined_key.rpartition(SEP)
                parts.setdefault(key, {})[name] = array

        tracks = {k: Track.fromdict(**v) for k, v in parts.items()}
        return cls(tracks, start_time, update_time)
