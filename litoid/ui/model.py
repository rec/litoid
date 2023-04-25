from litoid import log
from litoid.io.midi.message import ControlChange, MidiMessage
from litoid.io.recorder import Recorder
from litoid.state import instruments
import copy


class Model:
    def __init__(self, iname, path):
        self.all_presets = self._all_presets()
        self.iname_to_selected_preset = {k: None for k in self.all_presets}
        self.iname = iname
        self.dmx_recorder = Recorder('DMX', path and path / 'dmx.npz')
        self.midi_recorder = Recorder('MIDI', path and path / 'midi.npz')
        self.empty_preset = {}

    @property
    def iname(self):
        return self._iname

    @iname.setter
    def iname(self, iname):
        assert iname in self.all_presets, iname
        self._iname = iname

    @property
    def instrument(self):
        return instruments()[self.iname]

    @property
    def selected_preset_name(self):
        return self.iname_to_selected_preset[self.iname]

    @selected_preset_name.setter
    def selected_preset_name(self, name):
        if name is None or name in self.presets:
            self.iname_to_selected_preset[self.iname] = name
        else:
            log.error('Cannot set selected_preset_name to', name)

    @property
    def presets(self):
        return self.all_presets[self.iname]

    @property
    def selected_preset(self):
        return self.presets.get(self.selected_preset_name, self.empty_preset)

    def delete_selected(self):
        name, self.selected_preset_name = self.selected_preset_name, None
        if not name:
            log.error('No preset')
        elif self.selected_preset.pop(name, None) is None:
            log.error('Preset', name, 'strangely did not exist')
        else:
            return True

    def callback(self, m):
        if isinstance(m, MidiMessage):
            key_size = 2 if isinstance(m, ControlChange) else 1
            self.midi_recorder.record(m.data, key_size, m.time)

    @property
    def is_instrument_dirty(self):
        return self.instrument.presets != self.presets

    @property
    def is_dirty(self):
        return self.all_presets != self._all_presets()

    def save(self):
        self._save(self.iname)

    def save_all(self):
        for iname in self.all_presets:
            self._save(iname)

    def save_recorders(self):
        self.dmx_recorder.save()
        self.midi_recorder.save()

    def revert(self):
        self.presets.clear()
        self.presets.update(copy.deepcopy(self.instrument.presets))

    def _all_presets(self):
        return {k: copy.deepcopy(v.presets) for k, v in instruments().items()}

    def _save(self, iname):
        instrument = instruments()[iname]
        presets = self.all_presets[iname]
        old, new = instrument.user_presets, presets.maps[0]
        if old != new:
            old.clear()
            old.update(copy.deepcopy(new))
            instruments.save_user_presets(iname)
