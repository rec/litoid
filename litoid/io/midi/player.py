from .recorder import MidiRecorder
from .track import MidiTrack
from functools import cached_property, total_ordering
from litoid.util.timed_heap import TimedHeap
from typing import Callable
import datacls
import time

INFINITE = float('inf')


@datacls.mutable
class MidiPlayer:
    recorder: MidiRecorder
    callback: Callable = print
    offset_time: float = 0
    start_time: float = 0

    @cached_property
    def timed_heap(self) -> TimedHeap:
        return TimedHeap(self.players)

    @cached_property
    def players(self):
        kt = ((k, t) for k, t in self.record.tracks.items() if t)
        return [TrackPlayer(self. k, t) for k, t in kt]

    def start(self):
        self.start_time = time.time()
        self.timed_heap.start()

    @cached_property
    def net_offset_time(self) -> float:
        return self.offset_time + self.start_time - self.recorder.start_time

    def track_callback(self, track: 'TrackPlayer'):
        pass


@total_ordering
@datacls(frozen=False, order=False)
class TrackPlayer:
    player: MidiPlayer
    key: tuple[int, ...]
    track: MidiTrack
    position: int = 0

    def __len__(self):
        return len(self.track) - self.position

    @property
    def timestamp(self) -> float:
        return self.track.times[self.position] if self else INFINITE

    def __lt__(self, x) -> bool:
        return self.timestamp < x.timestamp

    def __call__(self):
        self.track_callback(self)
        self.position += 1
