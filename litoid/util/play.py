from pathlib import Path
from threading import Lock, Thread

import simpleaudio as sa
import xmod

DEFAULT = Path(__file__).parents[2] / 'audio/Click Mini 3.wav'
_RUNNING = False
_LOCK = Lock()


def play_now(filename=None):
    global _RUNNING
    with _LOCK:
        if _RUNNING:
            return
        _RUNNING = True

    wave_obj = sa.WaveObject.from_wave_file(str(filename or DEFAULT))
    wave_obj.play().wait_done()
    _RUNNING = False


@xmod
def play_later(filename=None):
    Thread(target=play_now, args=(filename,), daemon=True).start()
