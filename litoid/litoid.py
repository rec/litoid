# DEPRECATED

from . import app
from .state import state
from functools import cached_property
from pathlib import Path
import dtyper
import xmod


@xmod
@app.command()
def litoid(
    state_path: Path = app.Argument(None, help='Path to the state file'),
):
    import IPython
    litoid = Litoid(**locals())

    scope_vars = {'li': litoid, 'litoid': litoid}
    IPython.start_ipython(argv=[], user_ns=scope_vars)


@dtyper.dataclass(litoid)
class Litoid:
    @cached_property
    def state(self):
        return state(self.state_path)

    def __dir__(self):
        return sorted(set(dir(super()) + ['state'] + dir(self.state)))

    def __getattr__(self, k):
        return getattr(self.state, k)
