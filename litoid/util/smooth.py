import xmod
import pprint


@xmod
def smooth(it):
    value = time = None
    for i, (t, v) in enumerate(it):
        if i:
            print(i, t, v, value)
        if i and (jump := abs(value - v)) > 1:
            dt = (t - time) / jump
            dv = 1 if v > value else -1
            for i in range(1, jump):
                yield time + i * dt, value + i * dv
            pprint.pprint(locals())

        yield t, v
        time, value = t, v
