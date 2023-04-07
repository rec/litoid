from pathlib import Path
from functools import wraps
import inspect
import os
import sys
import xmod

ROOT = Path(__file__).parent
DEBUG = os.environ.get('DEBUG', '').strip().lower().startswith('t')


@xmod
def log(*a, file=sys.stderr, label='LOG', **ka):
    fname = Path(inspect.stack()[1][0].f_code.co_filename).relative_to(ROOT)
    print(f'{label + ":":6} {str(fname):16}', *a, file=file, **ka)


@wraps(log)
def error(*a, label='ERROR', **ka):
    log(*a, label=label, **ka)


@wraps(log)
def debug(*a, label='DEBUG', **ka):
    if DEBUG:
        log(*a, label=label, **ka)


if __name__ == '__main__':
    log('Regular log')
    error('An error line')
    debug('Debug')
