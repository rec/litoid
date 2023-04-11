from . import midi_message
from functools import cached_property
import datacls
import numpy as np
import time

INITIAL_SIZE = 16
RESIZE_RATIO = 2
SEP = '-'


@datacls.mutable
class MidiTrack:
    byte_width: int
    count: int = 0

    @cached_property
    def times(self):
        return np.empty(INITIAL_SIZE)

    @cached_property
    def data(self):
        return np.empty(INITIAL_SIZE * self.byte_width, dtype='uint8')

    def append(self, time, *data):
        assert self.byte_width == len(data)

        if self.count >= len(self.times):
            self.times.resize(RESIZE_RATIO * len(self.times))
            self.data.resize(RESIZE_RATIO * len(self.data))

        self.times[self.count] = time
        c = self.byte_width * self.count
        self.data[c:c + self.byte_width] = data

    def asdict(self):
        return {
            'data': self.data[0:self.byte_width * self.count],
            'times': self.times[0:self.count],
        }

    @classmethod
    def fromdict(cls, data, times):
        byte_width = len(data) // len(times)
        assert byte_width * len(data) == len(times)
        self = cls(byte_width)
        self.__data__.update(data=data, times=times)
        return self


class MidiRecorder:
    def __init__(self, tracks=None, first_time=None):
        self.tracks = {} if tracks is None else tracks
        self.first_time = first_time

    def start(self):
        self.first_time = time.time()

    def record(self, msg: midi_message.MidiMessage):
        if self.first_time is None:
            self.first_time = msg.time

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

        if self.first_time is not None:
            d['first_time'] = np.array([self.first_time])
        return d

    @classmethod
    def fromdict(cls, d):
        result = {}
        for subkey, v in d.items():
            if subkey != 'first_time':
                *key, k = subkey.split(SEP)
                key = tuple(int(i) for i in key)
                result.setdefault(key, {})[k] = v

        tracks = {k: MidiTrack.fromdict(**v) for k, v in result.items()}

        return cls(tracks, d.get('first_time'))
