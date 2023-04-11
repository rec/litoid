from . import midi_message
from functools import cached_property
import datacls
import numpy as np

INITIAL_SIZE = 16
RESIZE_RATIO = 2


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


class MidiRecorder:
    def __init__(self):
        self.tracks = {}

    def record(self, msg: midi_message.MidiMessage):
        keysize = 2 if isinstance(msg, midi_message.ControlChange) else 1
        key, data = msg.data[:keysize], msg.data[keysize:]
        if not (track := self.tracks.get(key)):
            track = MidiTrack(len(data))
            self.tracks[key] = track
        track.append(msg.time, *data)
