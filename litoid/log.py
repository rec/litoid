from .util import play
from pathlib import Path
from functools import wraps
import PySimpleGUI as sg
import inspect
import os
import sys
import xmod

ROOT = Path(__file__).parent
DEBUG = os.environ.get('DEBUG', '').strip().lower().startswith('t')
POPUP_ERRORS = False


def _log(label, *a, file=sys.stderr, **ka):
    for depth in (2, 3):
        frame = inspect.stack()[depth][0].f_code
        fname = Path(frame.co_filename)
        if ROOT in fname.parents:
            fname = fname.relative_to(ROOT)
            line_number = frame.co_firstlineno
            break
    else:
        fname = line_number = '?'

    file_position = f'{fname}:{line_number}'
    print(f'{label + ":":6} {file_position:16}', *a, file=file, **ka)


@xmod
@wraps(_log)
def log(*a, label='LOG', **ka):
    _log(label, *a, **ka)


@wraps(_log)
def error(*a, label='ERROR', **ka):
    play()
    _log(label, *a, **ka)
    if POPUP_ERRORS:
        sg.popup_auto_close(*a)


@wraps(_log)
def debug(*a, label='DEBUG', **ka):
    if DEBUG:
        _log(label, *a, **ka)


if __name__ == '__main__':
    log('Regular log')
    error('An error line')
    debug('Debug')
