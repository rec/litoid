from .level import Level
from collections import ChainMap
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
class Instrument:
    name: str
    channels: list[str, ...]
    value_names: dict = datacls.field(dict)
    builtin_presets: dict = datacls.field(dict)
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

    def _level_to_name(self, channel: Channel, level: int) -> str | None:
        if names := self._value_names.get(channel):
            return names.inv[level]

    @cached_property
    def presets(self) -> dict[str, dict]:
        return ChainMap(self.user_presets, self.builtin_presets)

    def map(self, ch: int | str, val: int | str) -> Level:
        if isinstance(ch, int):
            channel = ch
            channel_name = self.channels[channel]
        else:
            channel_name = ch
            channel = self._channels_inv[channel_name]
        if isinstance(val, int):
            value = val
            value_name = self._level_to_name(channel, val)
        else:
            value_name = val
            value = self._remap_value(channel_name, val)

        return Level(channel, channel_name, value, value_name)

    def remap_dict(self, levels: dict[str, int | str]):
        return dict(self._remap(c, v) for c, v in levels.items())

    def _remap_value(self, channel: str, value: int | str):
        if not isinstance(value, str):
            return value

        if (v := self._value_names.get(channel, {}).get(value)) is None:
            raise ValueError(f'Bad channel value {channel}, {value}')
        return v

    def _remap(self, channel: str, value: int | str) -> tuple[int, int]:
        return self._channels_inv[channel], self._remap_value(channel, value)

    @cached_property
    def blackout(self):
        return self.presets.get('blackout') or {}


def combine(target, *dicts):
    for d in dicts:
        target |= d
    return target
