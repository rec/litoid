from .. import log
import PySimpleGUI as sg
import pyperclip
import json


class Action:
    def __init__(self, controller, msg):
        self.controller = controller
        self.view = controller.view
        self.model = self.controller.model
        self.msg = msg

    def __call__(self):
        if self.msg.is_close:
            return

        if self.msg.key.startswith('+'):
            print(self.msg.key)
            return
        getattr(self, self.msg.action, self._unknown)()

    @property
    def _value(self):
        return self.msg.values.get(self.msg.key)

    def _set_channel_level(self, value):
        self.controller.set_channel_level(
            self.msg.name, self.msg.channel, value
        )

    def _unknown(self):
        log.error('Unknown key', self.msg.key))

    def blackout(self):
        self.controller.blackout(self.msg.name)

    def combo(self):
        self._set_channel_level(self._value)

    def copy(self):
        pyperclip.copy(self.controller.copy())

    def cut(self):
        if name := self.model.current_preset_name is None:
            log.error('No preset')
        else:
            try:
                del self.model.selected_preset[name]
            except Exception as e:
                log.error(e)
            else:
                self.copy()
            # TODO: must update selector here!

    def input(self):
        try:
            value = int(self._value)
        except Exception:
            value = 0
        self._set_channel_level(value)

    def menu(self):
        name = self._value.split()[0].strip('.').lower()
        method = getattr(self, name)
        method()

    def new(self):
        name = sg.popup_get_text('Enter new patch name')
        print(name)  # TODO

    def paste(self):
        self.controller.paste(pyperclip.paste())

    def preset(self):
        log.error()  # TODO
        # self.view.set_preset(self._value)

    def revert(self):
        self.model.revert()

    def save(self):
        self.model.save()

    def slider(self):
        self._set_channel_level(int(self._value))

    def tabgroup(self):
        tab, iname = self._value.split('.')
        assert tab == 'tab'
        self.model.iname = iname
        self.view.window.refresh()

    def redo(self):
        log.error()  # TODO

    def undo(self):
        log.error()  # TODO
