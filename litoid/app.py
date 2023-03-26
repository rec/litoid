from dtyper import Argument, Option, Typer

__all__ = 'Argument', 'Option', 'Typer', 'app', 'command'

app = Typer(
    add_completion=False,
    context_settings={'help_option_names': ['-h', '--help']},
)
command = app.command
