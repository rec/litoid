from ..util import file, read_write
from functools import cached_property
import datacls

Channel = int | str


class ValueNames(dict):
    def __init__(self, names: dict[str, int]):
        items = sorted((v, k) for k, v in names.items())
        super().__init__((k, v) for v, k in items)

        self.inv = []
        for (v1, k1), (v2, k2) in zip(items, items[1:] + [(256, None)]):
            self.inv.extend(k1 for i in range(v1, v2))


@datacls
class Instrument(read_write.ReadWrite):
    name: str
    channels: list[str, ...]
    value_names: dict = datacls.field(dict)
    presets: dict = datacls.field(dict)
    user_presets: dict = datacls.field(dict)

    @cached_property
    def _channels_inv(self):
        return {c: i for i, c in enumerate(self.channels)}

    @cached_property
    def _value_names(self) -> dict:
        d = {k: ValueNames(v) for k, v in self.value_names.items()}
        return self._add_inv(d)

    def _add_inv(self, d):
        return d | {self._channels_inv[k]: v for k, v in d.items()}

    def level_to_name(self, channel: Channel, level: int) -> str | None:
        return self.value_names[channel].inv[level]

    @cached_property
    def mapped_presets(self) -> dict[str, dict]:
        presets = self.presets | self.user_presets
        return {k: self.remap_dict(v) for k, v in presets.items()}

    def remap(self, channel: Channel, value: int | str) -> tuple[int, int]:
        if isinstance(channel, str):
            channel = self._channels_inv[channel]

        if isinstance(v := value, str):
            v = self._value_names.get(channel, {}).get(v)
            if v is None:
                raise ValueError(f'Bad channel value {channel}, {value}')
        return channel, v

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
