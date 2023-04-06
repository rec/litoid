from functools import cached_property
import PySimpleGUI as sg
import datacls


@datacls
class Message:
    """
    All message keys look like name.channel.action
    OR (soon) name.action
    """
    key: str
    values: list[str, ...] | None = None

    LITOID_CLOSE = 'litoid.(none).close'
    CLOSERS = sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT, LITOID_CLOSE

    @property
    def is_close(self):
        return self.key in self.CLOSERS

    @cached_property
    def name(self):
        name, channel, action = self.key.split('.')
        return name

    @cached_property
    def channel(self):
        name, channel, action = self.key.split('.')
        return channel

    @cached_property
    def action(self):
        """Return the name of the action"""
        name, channel, action = self.key.split('.')
        return action
