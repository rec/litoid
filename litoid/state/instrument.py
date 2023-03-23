from ..util.read_write import ReadWrite
from functools import cached_property
import tomlkit
import datacls


@datacls
class Instrument(ReadWrite):
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
        return combine([*splits, base, id1, id2])

    @cached_property
    def _value_names(self) -> tuple[dict, ...]:
        return tuple(self.value_names.get(c, {}) for c in self.channels)

    @cached_property
    def mapped_presets(self) -> dict[str, dict]:
        return {k: self.remap_dict(v) for k, v in self.presets.items()}

    def remap(self, channel: int | str, value: int | str) -> tuple[int, int]:
        if (cm := self.channel_map.get(channel)) is None:
            raise ValueError(f'Bad channel "{channel}"')
        if isinstance(cm, tuple):
            ch, spl = cm
        else:
            ch, spl = cm, None

        if not isinstance(v := value, int):
            if (v := self.value_names.get(ch, {}).get(value)) is None:
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
        return cls(**tomlkit.loads(open(filename)))


def combine(dicts):
    result = {}
    for d in dicts:
        result |= d
    return result
