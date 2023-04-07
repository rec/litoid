from ..state import instruments
from ..util.play import play_error
from functools import cached_property
import copy


class Model:
    def __init__(self, iname):
        self.iname = iname

    @property
    def iname(self):
        return getattr(self, '_iname', '')

    @iname.setter
    def iname(self, iname):
        assert iname in self.all_presets, iname
        self._iname = iname

    @cached_property
    def all_presets(self):
        return {k: copy.deepcopy(v.presets) for k, v in instruments().items()}

    @cached_property
    def selected_preset_names(self):
        return {k: None for k in self.all_presets}

    @property
    def selected_preset_name(self):
        return self.selected_preset_names[self.iname]

    @property
    def presets(self):
        return self.all_presets[self.iname]

    @property
    def selected_preset(self):
        return self.presets[self.selected_preset_name]

    def select_preset(self, name: str | None):
        assert name is None or name in self.presets
        self.selected_preset_names[self.iname] = name

    def save(self):
        play_error()  # TODO

    def revert(self):
        play_error()  # TODO
