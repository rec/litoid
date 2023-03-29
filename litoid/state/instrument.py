from ..util import file, read_write
from functools import cached_property
import datacls

Channel = int | str


@datacls
class Instrument(read_write.ReadWrite):
    name: str
    channels: list[str, ...]
    splits: dict = datacls.field(dict)
    value_names: dict = datacls.field(dict)
    presets: dict = datacls.field(dict)

    @cached_property
    def channel_map(self) -> dict[str, int]:
        base = {c: i for i, c in enumerate(self.channels)}
        id1 = {i: i for i, c in enumerate(self.channels)}
        id2 = {str(i): i for i, c in enumerate(self.channels)}

        def split(name, split):
            return {f'{c}_{name}': (i, split) for c, i in base.items()}

        splits = [split(n, s) for n, s in self.splits.items()]
        bases = base, id1, id2
        bases = [{k: (v, None) for k, v in b.items()} for b in bases]
        return combine(splits + bases)

    @cached_property
    def full_value_names(self) -> dict:
        def sort(d):
            items = sorted((v, k) for k, v in d.items())
            return {k: v for v, k in items}

        vn = {k: sort(v) for k, v in self.value_names.items()}
        return vn | {self.map_channel(k)[0]: v for k, v in vn.items()}

    def map_channel(self, channel:  Channel) -> tuple:
        if (cm := self.channel_map.get(channel)) is not None:
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
        ch, spl = self.map_channel(channel)
        if not isinstance(v := value, int):
            if (v := self.full_value_names.get(ch, {}).get(value)) is None:
                raise ValueError(f'Bad channel value {channel}, {value}')

        if spl:
            a, b = spl
            assert 0 <= a < b <= 255, f'[{a}, {b}]'
            v = round(a + ((b - a) * v) / 255)

        return ch, max(0, min(255, v))

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


def combine(dicts):
    result = {}
    for d in dicts:
        result |= d
    return result
