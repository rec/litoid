import IPython
from typer import Argument, Option, Typer

app = Typer(
    add_completion=False,
    context_settings={'help_option_names': ['-h', '--help']},
)
command = app.command


@command()
def main(
    host: str = Argument('localhost', help='Host to connect to.'),
):
    scope_vars = dict(locals())

    print('            LITOID')
    IPython.start_ipython(argv=[], user_ns=scope_vars)
    print('            litoid')



if __name__ == '__main__':
    app(standalone_mode=False)
