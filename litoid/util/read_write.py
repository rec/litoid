import tomllib
import tomlkit


class ReadWrite:
    @classmethod
    def read(cls, filename):
        return cls(**tomllib.loads(open(filename)))

    def write(self, filename):
        tomlkit.dump(self.asdict(), open(filename, 'w'))
