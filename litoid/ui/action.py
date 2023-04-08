from .. import log
import PySimpleGUI as sg
import pyperclip


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

    def _set_channel_level(self, *a):
        self.controller.set_channel_level(self.msg.name, self.msg.channel, *a)

    def _unknown(self):
        log.error('Unknown key', self.msg.key)

    def blackout(self):
        self.controller.blackout(self.msg.name)

    def combo(self):
        self._set_channel_level(self._value, 'combo')

    def copy(self):
        pyperclip.copy(self.controller.copy())

    def cut(self):
        if self.model.delete_selected():
            self.copy()
            self.view.update_selector()

    def input(self):
        try:
            value = int(self._value)
        except Exception:
            value = 0
        self._set_channel_level(value, 'input')

    def menu(self):
        name = self._value.split()[0].strip('.').lower()
        method = getattr(self, name)
        method()

    def new(self):
        name = sg.popup_get_text('Enter new preset name').strip()
        if name in self.model.presets:
            log.error('Preset', name, 'exists')
        elif name:
            self.model.presets[name] = self.controller.lamp.levels
            values = sorted(self.model.presets)
            self.view.update_presets(self.iname, values=values, value=name)

    def paste(self):
        self.controller.paste(pyperclip.paste())

    def preset(self):
        self.controller.set_preset(self._value)
        self.view.update_presets(self.iname, value=self._value)
        self.view.update_instrument(self.model.iname)

    def revert(self):
        ch = sg.popup_ok_cancel(
            f'Revert to saved for {self.iname}?',  title='Revert'
        )
        if ch == 'OK':
            self.model.revert()
        elif ch != 'Cancel':
            log.error(f'Got "{ch}", not OK or Cancel')

    def save(self):
        if self.model.is_dirty:
            self.model.save()
        else:
            log.error('Nothing to save')

    def slider(self):
        self._set_channel_level(int(self._value), 'slider')

    def tabgroup(self):
        tab, iname = self._value.split('.')
        assert tab == 'tab'
        self.model.iname = iname
