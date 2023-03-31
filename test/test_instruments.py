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

    assert len(vn := laser._value_names) == 6
    actual = sorted(str(i) for i in laser._value_names.keys())
    expected = ['0', '1', '8', 'color', 'mode', 'pattern']
    assert actual == expected

    assert laser._channels_inv['xrot'] == 3
