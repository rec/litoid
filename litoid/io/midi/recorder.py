from . import message
from . track import MidiTrack
import datacls
from litoid import log
import numpy as np
import time

SEP = '-'


@datacls.mutable
class MidiRecorder:
    tracks: dict = datacls.field(dict[tuple, MidiTrack])
    start_time: float = datacls.field(time.time)
    update_time: float = datacls.field(time.time)

    def record(self, msg: message.MidiMessage):
        keysize = 2 if isinstance(msg, message.ControlChange) else 1
        key = SEP.join(str(i) for i in msg.data[:keysize])

        if not (track := self.tracks.get(key)):
            track = MidiTrack(len(msg.data))
            self.tracks[key] = track

        track.append(msg.data, msg.time)
        self.update_time = msg.time

    def report(self):
        return {
            'event_count': sum(t.count for t in self.tracks.values()),
            'track_count': len(self.tracks),
        }

    def asdict(self):
        data = {'times': np.array((self.start_time, self.update_time))}

        for key, track in sorted(self.tracks.items()):
            for name, array in track.asdict().items():
                if len(array):
                    joined_key = SEP.join((key, name))
                    data[joined_key] = array
                else:
                    log.error(f'Empty track: {key=} {name=}')

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

        tracks = {k: MidiTrack.fromdict(**v) for k, v in parts.items()}
        return cls(tracks, start_time, update_time)
