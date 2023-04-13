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

    @property
    def first_time(self) -> float | None:
        return self.times[0] if len(self.times) else None

    def __len__(self):
        return self.count

    def __getitem__(self, i):
        b = i * self.byte_width
        return self.times[i], self.data[b:b + self.byte_width]

    def __setitem__(self, i, v):
        time, data = v
        self.times[i] = time
        b = i * self.byte_width
        self.data[b:b + self.byte_width] = data

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
