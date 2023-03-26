from . import app
from .state import state
from pathlib import Path
import IPython
import dtyper
import xmod


@xmod
@app.command()
def litoid(
    state_path: Path = app.Argument(None, help='Path to the state file'),
):
    litoid = Litoid(**locals())

    scope_vars = {'li': litoid, 'litoid': litoid}
    IPython.start_ipython(argv=[], user_ns=scope_vars)


@dtyper.dataclass(litoid)
class Litoid:
    def __post_init__(self):
        self.state = state(self.state_path)
