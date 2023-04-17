from .recorder import Recorder
from .track import Track
from functools import cached_property, total_ordering
from litoid.util.timed_heap import TimedHeap
from typing import Callable
import datacls
import time

INFINITE = float('inf')


@datacls.mutable
class Player:
    recorder: Recorder
    callback: Callable = print
    offset_time: float = 0
    start_time: float = 0

    @cached_property
    def timed_heap(self) -> TimedHeap:
        kt = ((k, t) for k, t in self.record.tracks.items() if t)
        players = (TrackPlayer(self, k, t) for k, t in kt)
        return TimedHeap([tp for tp in players if tp])

    def start(self):
        self.start_time = time.time()
        self.timed_heap.start()

    @cached_property
    def net_offset(self) -> float:
        return self.offset_time + self.start_time - self.recorder.start_time


@total_ordering
@datacls.mutable(order=False)
class TrackPlayer:
    player: Player
    key: tuple[int, ...]
    track: Track
    position: int = 0

    def __len__(self):
        return len(self.track) - self.position

    @property
    def timestamp(self) -> float:
        if not self:
            return INFINITE
        return self._timestamp() + self.player.net_offset

    def __lt__(self, x) -> bool:
        return self._timestamp() < x._timestamp()

    def _timestamp(self):
        return self.track.times[self.position]

    def __call__(self):
        msg_data = self.track.get_message(self.position)
        self.position += 1

        self.player.callback(self.key, msg_data)

        if self:
            self.player.timed_heap.push(self)
