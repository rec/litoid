from litoid.state import instruments


def test_instruments():
    names, ins = zip(*sorted(instruments().items()))
    assert list(names) == ['gantom', 'laser']
    gantom, laser = ins

    assert len(vn := laser._value_names) == 6
    actual = sorted(str(i) for i in laser._value_names.keys())
    expected = ['0', '1', '8', 'color', 'mode', 'pattern']
    assert actual == expected

    assert laser._channels_inv['xrot'] == 3
