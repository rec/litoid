import xmod

SYSEX_STATUS = 0xF0


def has_channel(status):
    return status < SYSEX_STATUS


@xmod
class MidiMessage:
    fields = ()
    status_start = 0

    __slots__ = 'data', 'time'

    def __init__(self, data=None, time=0, *, data_maker=tuple, **kwargs):
        if data is None:
            data = data_maker(kwargs.pop(f, 0) for f in self.fields)
            if kwargs:
                s = 's' * (len(kwargs) != 1)
                raise ValueError(f'Unknown parameter{s}: {sorted(kwargs)}')

        self.data = data
        self.time = time

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    @property
    def status(self):
        return self.data[0]

    def asdict(self):
        return {k: getattr(self, k) for k in self.fields}

    @classmethod
    def fromdict(cls, *, data_maker=list, **kwargs):
        assert len(kwargs) == len(cls.fields)
        fields = data_maker(kwargs[f] for f in cls.fields)
        return cls(fields)

    def __new__(cls, data=None, time=0, **kwargs):
        if data is not None and kwargs:
            raise ValueError('Cannot specify data and named args together')

        try:
            cls = MESSAGE_CLASSES[data[0] - 128]
        except IndexError:
            cls = None

        if cls is None:
            raise ValueError(f'{data=} is not a MIDI packet')

        if cls.status_start != SYSEX_STATUS:
            if len(data) != 1 + len(cls.fields):
                raise ValueError(
                    'Midi packet has wrong data length'
                    f'{len(data)=} != 1 + {len(cls.fields)=} '
                )

        self = super().__new__(cls)
        cls.__init__(self, data, time, **kwargs)
        return self


class MidiChannelMessage(MidiMessage):
    def __init__(self, data=None, time=0, *, channel=0, **kwargs):
        status = channel + self.status_start
        super().__init__(data, time, status=status, **kwargs)

    @property
    def channel(self):
        return self.status & 0x0F

    @channel.setter
    def channel(self, channel):
        self.status = (self.status & 0xF0) | channel

    def asdict(self):
        return super().asdict() | {'channel': self.channel}

    @classmethod
    def fromdict(cls, name, channel, **kwargs):
        status = cls.status_start + channel
        return super().fromdict(name, status=status, **kwargs)


def _class(status_start, name, *fields):
    parent, init = _parent_init(status_start, fields)

    props = {field: _prop(i + 1, field) for i, field in enumerate(fields)}
    class_vars = {'fields': fields, 'status_start': status_start}

    members = {'__init__': init, **props, **class_vars}
    cls = type(name, (parent,), members)
    globals()[name] = cls
    return cls


def _prop(i, field):
    def getter(self):
        return self.data[i]

    def setter(self, d):
        self.data[i] = d

    getter.__name__ = setter.__name__ = field
    return property(getter, setter)


def _parent_init(status_start, fields):
    if has_channel(status_start):
        parent = MidiChannelMessage
        params = 'channel', *fields
    else:
        parent = MidiMessage
        params = fields

    # Construct the constructor!
    if params_in := ', '.join(f'{p}=0' for p in params):
        params_in = f', *, {params_in}'

    if params_out := ', '.join(f'{p}={p}' for p in params):
        params_out = f', {params_out}'

    definition = f'lambda self, data=None, time=0{params_in}:'
    result = f'{parent.__name__}.__init__(self, data, time{params_out})'
    definition = f'{definition} {result}'

    init_f = eval(definition)
    init_f.__name__ = '__init__'
    return parent, init_f


_CHANNEL = (
    # Channel messages
    _class(0x80, 'NoteOff', 'note', 'velocity'),
    _class(0x90, 'NoteOn', 'note', 'velocity'),
    _class(0xa0, 'Polytouch', 'note', 'value'),
    _class(0xb0, 'ControlChange', 'control', 'value'),
    _class(0xc0, 'ProgramChange', 'program'),
    _class(0xd0, 'Aftertouch', 'value'),
    _class(0xe0, 'Pitchwheel', 'pitch'),
)

_SYSTEM = (
    # System common messages.
    _class(0xf0, 'Sysex'),
    _class(0xf1, 'QuarterFrame', 'frame_type', 'frame_value'),
    _class(0xf2, 'Songpos', 'pos'),
    _class(0xf3, 'SongSelect', 'song'),

    None,  # 0xf4 is undefined
    None,  # 0xf5 is undefined
    _class(0xf6, 'TuneRequest'),
    None,  # 0xf7 is undefined

    # System real time messages.
    _class(0xf8, 'Clock'),
    None,  # 0xf9 is undefined
    _class(0xfa, 'Start'),
    _class(0xfb, 'Continue'),

    _class(0xfc, 'Stop'),
    None,  # 0xfd is undefined
    _class(0xfe, 'ActiveSensing'),
    _class(0xff, 'Reset'),
)

MESSAGE_CLASSES = tuple(c for c in _CHANNEL for i in range(16)) + _SYSTEM
__all__ = ('MidiMessage',) + tuple(c.__name__ for c in _CHANNEL + _SYSTEM if c)
