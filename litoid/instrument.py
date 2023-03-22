from functools import cached_property
import datacls


@datacls
class Instrument:
    channels: list[str, ...]
    splits: dict = datacls.field(dict)
    value_names: dict = datacls.field(dict)
    presets: dict = datacls.field(dict)

    @cached_property
    def to_channel(self) -> dict[str, int]:
        basic = {c: i for i, c in enumerate(self.channels)}
        identity = {i: i for i, c in enumerate(self.channels)}

        to_channel = {c: (i, None) for c, i in (basic | identity).items()}
        for name, spl in self.splits.items():
            to_channel |= {f'{c}_{name}': (i, spl) for c, i in basic.items()}

        return to_channel

    @cached_property
    def _value_namesl(self) -> tuple[dict, ...]:
        return tuple(self.value_names.get(c, {}) for c in self.channels)

    def remap(self, channel: int | str, value: int | str) -> tuple[int, int]:
        if ch_spl := self.to_channel.get(channel):
            ch, spl = ch_spl
        else:
            raise ValueError(f'Bad channel {channel}')

        if not isinstance(v := value, int):
            if (v := self._value_names.get(ch, {}).get(value)) is None:
                raise ValueError(f'Bad channel value {channel}, {value}')

        if spl:
            a, b = spl
            assert 0 <= a < b <= 255, f'[{a}, {b}]'
            v = round(a + ((b - a) * v) / 255)

        return ch, max(0, min(255, v))

    def remap_dict(self, levels: dict):
        return dict(self.remap(c, v) for c, v in levels.items())

    def to_tuple(self, levels: dict):
        return tuple(levels.get(i, 0) for i in range(len(self.channels)))

    @cached_property
    def default(self) -> dict:
        return self.remap_dict(self.presets.get('default', {}))

    @cached_property
    def default_tuple(self) -> tuple[int]:
        return self.to_tuple(self.default)


def combine(dicts):  # not used
    result = {}
    for d in dicts:
        result |= d
    return result
