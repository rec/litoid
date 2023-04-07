from .util import play
from pathlib import Path
from functools import wraps
import inspect
import os
import sys
import xmod

ROOT = Path(__file__).parent
DEBUG = os.environ.get('DEBUG', '').strip().lower().startswith('t')


def _log(label, *a, file=sys.stderr, **ka):
    frame = inspect.stack()[2][0].f_code
    fname = Path(frame.co_filename).relative_to(ROOT)
    # print(dir(frame))
    line_number = frame.co_firstlineno
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


@wraps(_log)
def debug(*a, label='DEBUG', **ka):
    if DEBUG:
        _log(label, *a, **ka)


if __name__ == '__main__':
    log('Regular log')
    error('An error line')
    debug('Debug')