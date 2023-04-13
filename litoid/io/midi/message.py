import clsprop
import xmod

_PITCH = 0xe0
_SYSEX = 0xF0


@xmod
class MidiMessage:
    fields = ()
    status_start = 0

    __slots__ = 'data', 'time'

    def __init__(self, data=None, time=0, **kwargs):
        self.time = time

        if data is not None:
            self.data = data
        else:
            self.data = (
                [self.status_start]
                + [kwargs.pop(f, 0) or 0 for f in self.fields]
            )

        if bad := [k for k, v in kwargs.items() if v is not None]:
            assert (data is None) or not kwargs, f'{data=} {kwargs=}'
            s = 's' * (len(bad) != 1)
            raise ValueError(f'Extra parameter{s}: {list(kwargs)}')

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        return self.data[i]

    @clsprop
    def has_channel(cls) -> bool:
        return _has_channel(cls.status_start)

    @clsprop
    def size(cls) -> int:
        return (
            len(cls.fields)
            + (not cls.has_channel)
            + (cls.status_start == _PITCH)
        )

    @property
    def status(self):
        return self.data[0]

    def asdict(self):
        return {k: getattr(self, k) for k in self.fields}

    def __new__(cls, data=None, time=0, **kwargs):
        if data is not None and kwargs:
            raise ValueError('Cannot specify data and named args together')

        try:
            cls = MESSAGE_CLASSES[data[0] - 128]
        except IndexError:
            cls = None

        if cls is None:
            raise ValueError(f'{data=} is not a MIDI packet')

        if cls.status_start != _SYSEX and len(data) != cls.size:
            msg = f'Wrong MIDI packet length: {len(data)} != {cls.size}'
            raise ValueError(msg)

        self = super().__new__(cls)
        cls.__init__(self, data, time, **kwargs)
        return self


class MidiChannelMessage(MidiMessage):
    def __init__(self, data=None, time=0, **kwargs):
        channel = kwargs.pop('channel', None)

        if is_pitch := self.status_start == _PITCH:
            pitch = kwargs.pop('pitch', 0)
        super().__init__(data, time, **kwargs)
        if is_pitch:
            self.pitch = pitch
        if channel is not None:
            self.channel = channel

    @property
    def channel(self):
        return self.status & 0x0F

    @channel.setter
    def channel(self, channel):
        self.status = (self.status & 0xF0) | channel

    def asdict(self):
        return super().asdict() | {'channel': self.channel}


def _has_channel(status: int) -> bool:
    return status < _SYSEX


def _class(status_start, name, *props):
    if _has_channel(status_start):
        parent = MidiChannelMessage
        if status_start == _PITCH:
            fields = 'pitch',

        fields = 'channel', *props
    else:
        parent = MidiMessage
        fields = props

    members = {
        '__init__': _init(parent, fields),
        '__repr__': _repr(fields),
        'fields': fields,
        'status_start': status_start,
    }

    props = {prop: _prop(i + 1, prop) for i, prop in enumerate(props)}
    cls = type(name, (parent,), members | _pitch(status_start) | props)
    globals()[name] = cls
    return cls


def _prop(i, field):
    def getter(self):
        return self.data[i]

    def setter(self, d):
        self.data[i] = d

    getter.__name__ = setter.__name__ = field
    return property(getter, setter)


def _init(parent, fields):
    # Construct the constructor!
    if params_in := ', '.join(f'{f}=None' for f in fields):
        params_in = f', *, {params_in}'

    if params_out := ', '.join(f'{f}={f}' for f in fields):
        params_out = f', {params_out}'

    definition = f'lambda self, data=None, time=0{params_in}:'
    result = f'{parent.__name__}.__init__(self, data, time{params_out})'
    init = eval(f'{definition} {result}')
    init.__name__ = '__init__'
    return init


def _pitch(status_start):
    if status_start != _PITCH:
        return {}

    pitch_offset = 0x2000

    def getter(self):
        return 0x80 * self.pitch_hsb + self.pitch_lsb - self.pitch_offset

    def setter(self, p):
        self.pitch_hsb, self.pitch_lsb = divmod(p + self.pitch_offset, 0x80)

    return {
        'pitch': property(getter, setter),
        'pitch_offset': pitch_offset,
    }


def _repr(fields):
    # See dataclasses.py around line 595
    fields = *fields, 'time'
    params = ', '.join(f'{f}={{self.{f}!r}}' for f in fields)
    classname = '{self.__class__.__qualname__}'
    rep = eval(f'lambda self: f"{classname}({params})"')
    rep.__name__ = '__repr__'
    return rep


_CHANNEL = (
    # Channel messages
    _class(0x80, 'NoteOff', 'note', 'velocity'),
    _class(0x90, 'NoteOn', 'note', 'velocity'),
    _class(0xa0, 'Polytouch', 'note', 'value'),
    _class(0xb0, 'ControlChange', 'control', 'value'),
    _class(0xc0, 'ProgramChange', 'program'),
    _class(0xd0, 'Aftertouch', 'value'),
    _class(_PITCH, 'Pitch', 'pitch_lsb', 'pitch_hsb'),
)

_SYSTEM = (
    # System common messages.
    _class(_SYSEX, 'Sysex'),
    _class(0xf1, 'QuarterFrame', 'frame_type', 'frame_value'),
    _class(0xf2, 'Songpos', 'pos'),
    _class(0xf3, 'SongSelect', 'song'),

    None,  # 0xf4
    None,  # 0xf5
    _class(0xf6, 'TuneRequest'),
    None,  # 0xf7 is sysex end

    # System real time messages.
    _class(0xf8, 'Clock'),
    None,  # 0xf9
    _class(0xfa, 'Start'),
    _class(0xfb, 'Continue'),

    _class(0xfc, 'Stop'),
    None,  # 0xfd
    _class(0xfe, 'ActiveSensing'),
    _class(0xff, 'Reset'),
)

MESSAGE_CLASSES = tuple(c for c in _CHANNEL for i in range(16)) + _SYSTEM
__all__ = ('MidiMessage',) + tuple(c.__name__ for c in _CHANNEL + _SYSTEM if c)
