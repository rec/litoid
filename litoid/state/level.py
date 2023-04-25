from typing import NamedTuple


class Level(NamedTuple):
    channel: int
    channel_name: str
    value: int
    value_name: int | None
