from functools import cached_property
import PySimpleGUI as sg
import datacls


@datacls
class Message:
    """
    message format:

        action[.name[.channel]]

    """
    key: str
    values: list[str, ...] | None = None

    CLOSERS = sg.WIN_CLOSED, sg.WINDOW_CLOSE_ATTEMPTED_EVENT

    @property
    def is_close(self):
        return self.key in self.CLOSERS

    @cached_property
    def action(self):
        return self.key.split('.')[0]

    @cached_property
    def name(self):
        return (self.key.split('.') + [''])[1]

    @cached_property
    def channel(self):
        return (self.key.split('.') + ['', ''])[2]
