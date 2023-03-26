from ..util import file
import tomlkit


class ReadWrite:
    @classmethod
    def read(cls, filename):
        return cls(**file.load(filename))

    def write(self, filename):
        tomlkit.dump(self.asdict(), open(filename, 'w'))
