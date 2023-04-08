from .. import log
from ..state import instruments
import copy


class Model:
    def __init__(self, iname):
        it = instruments().items()
        self.all_presets = {k: copy.deepcopy(v.presets) for k, v in it}
        self.iname_to_selected_preset = {k: None for k, v in it}
        self.iname = iname

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
        assert name is None or name in self.presets
        self.iname_to_selected_preset[self.iname] = name

    @property
    def presets(self):
        return self.all_presets[self.iname]

    @property
    def selected_preset(self):
        return self.presets.get(self.selected_preset_name)

    def delete_selected(self):
        name, self.selected_preset_name = self.selected_preset_name, None
        if not name:
            log.error('No preset')
        elif self.selected_preset.pop(name, None) is None:
            log.error('Preset', name, 'strangely did not exist')
        else:
            return True

    @property
    def is_dirty(self):
        return self.instrument.presets != self.presets

    def save(self):
        old, new = self.instrument.user_presets, self.presets.map[0]
        old.clear()
        old.update(copy.deepcopy(new))
        instruments.save_user_presets(self.iname)

    def revert(self):
        self.presets.clear()
        self.presets.update(copy.deepcopy(self.instrument.presets))
