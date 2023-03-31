from ..util import file
from .instrument import Instrument
from functools import cache
from pathlib import Path
import xmod

__all__ = 'instruments',

ROOT = Path(__file__).parents[2]
DATA = ROOT / 'data'
assert DATA.exists()


@xmod
@cache
def instruments():
    def files(suffix):
        files = sorted(DATA.glob(f'*-{suffix}.toml'))
        return {f.stem.split('-')[0]: file.load(f) for f in files}

    defs = files('def')
    presets = files('presets')

    assert defs.keys() == presets.keys()
    kdp = zip(defs.keys(), defs.values(), presets.values())
    instruments = {k: Instrument(k, user_presets=p, **d) for k, d, p in kdp}
    return instruments


LASER = instruments()['laser']
GANTOM = instruments()['gantom']
