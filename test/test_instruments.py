from litoid.state import instruments


def test_instruments():
    names, ins = zip(*sorted(instruments().items()))
    assert list(names) == ['gantom', 'laser']
    gantom, laser = ins

    mapped_presets = {
        'default': {
            0: 192, 1: 0, 2: 64, 3: 64, 4: 64, 5: 64, 6: 64, 7: 64, 8: 128
        }
    }
    assert laser.mapped_presets == mapped_presets

    assert len(cm := laser.channel_map) == 45
    assert cm['xrot_abs'] == (3, [0, 127])
    assert cm['xrot'] == 3
