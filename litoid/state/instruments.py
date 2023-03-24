from .instrument import Instrument
from functools import cache
from pathlib import Path
import tomllib
import xmod

__all__ = 'LASER', 'GANTOM'

ROOT = Path(__file__).parents[2]
DATA = ROOT / 'data'
assert DATA.exists()


@xmod
@cache
def instruments():
    files = sorted(DATA.glob('*.toml'))
    return {f.stem: Instrument(**tomllib.loads(f.read_text())) for f in files}


LASER = instruments()['laser']
GANTOM = instruments()['gantom']