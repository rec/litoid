class MidiMessage:
    fields = ()
    status_start = 0
    data_type = tuple

    __slots__ = 'data', 'time'

    def __init__(self, data, time=0):
        self.data = data
        self.time = time

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    def asdict(self):
        return {k: getattr(self, k) for k in self.fields}

    @classmethod
    def fromdict(cls, **kwargs):
        assert len(kwargs) == len(cls.fields)
        fields = cls.data_type(kwargs[f] for f in cls.fields)
        return cls(fields)

    def __new__(cls, data, time=0):
        try:
            cls = MESSAGE_CLASSES[data[0] - 128]
        except IndexError:
            cls = None
        if cls is None:
            raise ValueError(f'{data=} is not a MIDI packet')
        if len(data) != len(cls.fields):
            raise ValueError('Midi packet has wrong data length')
        self = super().__new__(cls)
        cls.__init__(self, data, time=time)
        return self


class MidiChannelMessage(MidiMessage):
    @property
    def channel(self):
        return self.status & 0xF

    def asdict(self):
        return super().asdict() | {'channel': self.channel}

    @classmethod
    def fromdict(cls, name, channel, **kwargs):
        status = cls.status_start + channel
        return super().fromdict(name, status=status, **kwargs)


def _class(status_start, name, *fields):
    def prop(i, field):
        def fn(self):
            return self.data[i]

        fn.__name__ = field
        return property(fn)

    fields = 'status', *fields
    props = {field: prop(i, field) for i, field in enumerate(fields)}
    class_vars = {'fields': fields, 'status_start': status_start}

    parent = MidiChannelMessage if status_start < 0xF0 else MidiMessage
    cls = type(name, (parent,), props | class_vars)
    globals()[name] = cls
    return cls


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
    _class(0xf0, 'Sysex', 'data'),
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
