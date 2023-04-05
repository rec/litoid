from threading import Thread
from pathlib import Path
import inspect
import xmod
import simpleaudio as sa

DEFAULT = Path(__file__).parents[2] / 'audio/Click Mini 3.wav'


def play_now(filename=None):
    wave_obj = sa.WaveObject.from_wave_file(str(filename or DEFAULT))
    wave_obj.play().wait_done()


@xmod
def play_later(filename=None):
    Thread(target=play_now, args=(filename,), daemon=True).start()


def play_error(*messages, filename=None):
    play_later(filename)
    if not messages:
        messages = (inspect.currentframe().f_back.f_code.co_name,)
    print('ERROR', *messages)
