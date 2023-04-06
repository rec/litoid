from ..state import instruments
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
        assert iname in instruments(), iname
        self._iname = iname

    @cached_property
    def all_presets(self):
        return {k: copy.deepcopy(v.presets) for k, v in instruments().items()}

    @cached_property
    def current_presets(self):
        return {k: None for k in self.all_presets}
