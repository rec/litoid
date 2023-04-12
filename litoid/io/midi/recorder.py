from . import midi_message
from . track import MidiTrack
import datacls
import numpy as np
import time

SEP = '-'


@datacls.mutable
class MidiRecorder:
    tracks: dict = datacls.field(dict)
    start_time: float = datacls.field(time.time)

    def record(self, msg: midi_message.MidiMessage):
        keysize = 2 if isinstance(msg, midi_message.ControlChange) else 1
        key, data = msg.data[:keysize], msg.data[keysize:]
        if not (track := self.tracks.get(key)):
            track = MidiTrack(len(data))
            self.tracks[key] = track
        track.append(msg.time, *data)

    def asdict(self):
        d = {}

        for key, track in sorted(self.tracks.items()):
            key = SEP.join(str(i) for i in key)
            for k, v in track.asdict().items():
                subkey = SEP.join((key, k))
                d[subkey] = v

        if self.start_time is not None:
            d['start_time'] = np.array([self.start_time])
        return d

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
