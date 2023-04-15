from functools import cached_property
import datacls
import numpy as np

INITIAL_SIZE = 0x200
RESIZE_RATIO = 1.5


@datacls.mutable
class MidiTrack:
    byte_width: int
    count: int = 0

    @cached_property
    def times(self):
        return np.empty(INITIAL_SIZE, dtype='float64')

    @cached_property
    def data(self):
        return np.empty(INITIAL_SIZE * self.byte_width, dtype='uint8')

    @property
    def first_time(self) -> float | None:
        return self.times[0] if len(self.times) else None

    def get_message(self, i) -> tuple[np.ndarray, float]:
        b = i * self.byte_width
        return self.data[b:b + self.byte_width]

    def append(self, data: np.ndarray, time: float):
        assert self.byte_width == len(data)

        if self.count >= len(self.times):
            _resize(self.data, self.times)

        b = self.count * self.byte_width
        self.data[b:b + self.byte_width] = data
        self.times[self.count] = time

        self.count += 1

    def asdict(self):
        return {
            'data': self.data[0:self.byte_width * self.count],
            'times': self.times[0:self.count],
        }

    @classmethod
    def fromdict(cls, data, times):
        byte_width = len(data) // len(times)
        assert byte_width * len(times) == len(data)

        self = cls(byte_width)
        self.__dict__.update(data=data, times=times)
        return self


def _resize(*arrays):
    for a in arrays:
        a.resize(round(len(a) * RESIZE_RATIO + 0.5))
