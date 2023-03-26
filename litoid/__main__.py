import datacls
import IPython
from dtyper import Argument, Option, Typer
from pathlib import Path

app = Typer(
    add_completion=False,
    context_settings={'help_option_names': ['-h', '--help']},
)
command = app.command

assert Argument, Option


@datacls.mutable
class Litoid:
    """
    Help is on the way.
    """

    state_path: Path | None


@command()
def main(
    state_path: Path = Argument(None, help='Path to the state file'),
):
    litoid = Litoid(**locals())
    scope_vars = {'lit': litoid, **locals()}

    print('            LITOID')
    IPython.start_ipython(argv=[], user_ns=scope_vars)
    print('            litoid')


if __name__ == '__main__':
    app(standalone_mode=False)
