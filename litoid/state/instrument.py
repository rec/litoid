from ..util import file, read_write
from functools import cached_property
from typing import Self
import datacls

Channel = int | str
FULL_RANGE = 0, 255


@datacls(slots=True)
class ChannelRange:
    channel: int = 0
    range: tuple = FULL_RANGE

    def sub(self, range_: tuple) -> Self:
        return ChannelRange(self.channel, range_)

    def scale(self, v: int | float):
        if self.range != FULL_RANGE:
            a, b = self.range
            v = round(a + ((b - a) * v) / 255)
        return max(0, min(255, v))


@datacls
class Instrument(read_write.ReadWrite):
    name: str
    channels: list[str, ...]
    ranges: dict = datacls.field(dict)
    value_names: dict = datacls.field(dict)
    presets: dict = datacls.field(dict)

    @cached_property
    def channel_ranges(self) -> dict[str, int]:
        base = {c: ChannelRange(i) for i, c in enumerate(self.channels)}
        id1 = {i: ChannelRange(i) for i, c in enumerate(self.channels)}
        id2 = {str(i): ChannelRange(i) for i, c in enumerate(self.channels)}

        def channel_ranges(n, r):
            return {f'{c}_{n}': cr.replace(range=r) for c, cr in base.items()}

        ranges = [channel_ranges(n, r) for n, r in self.ranges.items()]
        r = combine(base, id1, id2, *ranges)
        assert 1 in id1
        assert 1 in r and '1' in r
        return r

    @cached_property
    def full_value_names(self) -> dict:
        def sort(d):
            items = sorted((v, k) for k, v in d.items())
            return {k: v for v, k in items}

        vn = {k: sort(v) for k, v in self.value_names.items()}
        return vn | {self.map_channel(k).channel: v for k, v in vn.items()}

    def map_channel(self, channel:  Channel) -> tuple:
        if (cm := self.channel_ranges.get(channel)) is not None:
            return cm
        raise ValueError(f'Bad channel "{channel}"')

    def level_to_name(self, channel: Channel, level: int) -> str | None:
        if names := self.full_value_names.get(channel):
            for k, v in reversed(names.items()):
                if v <= level:
                    return k

    @cached_property
    def mapped_presets(self) -> dict[str, dict]:
        return {k: self.remap_dict(v) for k, v in self.presets.items()}

    def remap(self, channel: Channel, value: int | str) -> tuple[int, int]:
        cr = self.map_channel(channel)
        if not isinstance(v := value, int):
            v = self.full_value_names.get(cr.channel, {}).get(value)
            if v is None:
                raise ValueError(f'Bad channel value {channel}, {value}')
        return cr.channel, cr.scale(v)

    def remap_dict(self, levels: dict):
        return dict(self.remap(c, v) for c, v in levels.items())

    @cached_property
    def blackout(self):
        return self.mapped_presets.get('blackout') or self.default

    @cached_property
    def default(self):
        return self.mapped_presets.get('default') or {}

    @classmethod
    def read(cls, filename):
        return cls(filename.stem, **file.load(filename))


def combine(target, *dicts):
    for d in dicts:
        target |= d
    return target
