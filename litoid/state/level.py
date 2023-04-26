from typing import NamedTuple


class Level(NamedTuple):
    channel: int
    channel_name: str
    value: int
    value_name: int | None

    @property
    def canonical_value(self):
        return self.value_name or self.value

    @property
    def cv(self):
        return self.channel, self.value
