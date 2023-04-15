from . import message
from . track import MidiTrack
import datacls
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
            track = MidiTrack(len(self.data))
            self.tracks[key] = track

        track.append(msg.data, msg.time)
        self.update_time = msg.time

    def asdict(self):
        data = {}
        times = np.array((self.start_time, self.update_time))

        for key, track in sorted(self.tracks.items()):
            for k, v in track.asdict().items():
                subkey = SEP.join((key, k))
                data[subkey] = v

        return {'data': data, 'times': times}

    @classmethod
    def fromdict(cls, d):
        result = {}
        for subkey, v in d.items():
            if subkey != 'start_time':
                *key, k = subkey.split(SEP)
                key = tuple(int(i) for i in key)
                result.setdefault(key, {})[k] = v

        tracks = {k: MidiTrack.fromdict(**v) for k, v in result.items()}

        return cls(tracks, d.get('start_time'))
