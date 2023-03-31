from . import lamp_page, ui
from ..io import midi
from ..state import scene, state as _state
import PySimpleGUI as sg
import datacls


@datacls.mutable
class InstrumentEditorApp(ui.UI):
    state: _state.State = datacls.field(_state)

    lamp = None
    preset = None

    @property
    def lamps(self):
        return self.state.lamps

    @property
    def instrument(self):
        return self.lamp.instrument

    def callback(self, msg):
        print(msg.key)
        *rest, el = msg.key.split('.')

        if el == 'tabgroup':
            name = msg.values['tabgroup'].split('.')[0]
            self.lamp = self.lamps[name]
            return

        if el == 'blackout':
            self.lamp.blackout()
            self.reset_levels()
            return

        try:
            new_value = msg.values[msg.key]

        except Exception:
            return

        def set_value(key, value):
            k = f'{lamp_name}.{ch}.{key}'
            msg.values[k] = value
            self.window[k].update(value=value)

        def set_all(new_value):
            try:
                level = max(0, min(255, int(new_value)))
            except (ValueError, TypeError):
                level = 0

            set_value('input', level)
            if ch_names:
                set_value('combo', self.instrument.level_to_name(ch, level))
            else:
                set_value('slider', level)

        if el == 'preset':
            self.preset = new_value
            self.lamp.send_preset(new_value)

        lamp_name, ch = rest
        ch_names = self.instrument.value_names.get(ch)

        if el == 'slider':
            set_value('input', level := int(new_value))

        elif el == 'combo':
            set_value('input', level := ch_names[new_value])

        elif el == 'input':
            set_all(new_value)

        else:
            print('unknown', msg.key)

        self.lamp[ch] = level

    def layout(self):
        def tab(lamp):
            return sg.Tab(lamp.name, lamp_page(lamp), k=f'{lamp.name}.tab')

        lamps = list(self.lamps.values())
        tabs = [tab(lamp) for lamp in lamps]
        self.lamp = lamps[0]

        return [[sg.TabGroup([tabs], enable_events=True, k='tabgroup')]]

    def start(self):
        self.state.blackout()
        self.state.set_scene(MidiScene(self))
        self.state.midi_input.start()
        try:
            super().start()
        finally:
            for lamp in self.state.lamps.values():
                lamp.blackout()

    def set_level(self, ch, v):
        if ch < len(self.lamp):
            if self.lamp[ch] == v:
                return
            self.lamp[ch] = v
            self.reset_level(ch)

    def reset_level(self, ch):
        v = self.lamp[ch]
        channel = self.lamp.instrument.channels[ch]
        k = f'{self.lamp.name}.{channel}.'
        self.window[k + 'input'].update(value=v)
        if (name := self.lamp.instrument.level_to_name(ch, v)) is not None:
            self.window[k + 'combo'].update(value=name)
        else:
            self.window[k + 'slider'].update(value=v)

    def reset_levels(self):
        for i in range(len(self.lamp.instrument.channels)):
            self.reset_level(i)


class MidiScene(scene.Scene):
    def __init__(self, ie):
        self.ie = ie

    def callback(self, state: _state.State, m: object) -> bool:
        if (
            isinstance(m, midi.Message)
            and m.type == 'control_change'
            and m.channel == 0
            and (m.control <= 18)  # or 50 <= m.control <= 68)
        ):
            d = m.control >= 10
            channel = m.control - d * 10
            value = m.value + 128 * d
            self.ie.set_level(channel, value)


def main():
    app = InstrumentEditorApp()
    app.start()


if __name__ == "__main__":
    main()
