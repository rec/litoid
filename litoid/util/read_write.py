import tomlkit


class ReadWrite:
    @classmethod
    def read(cls, filename):
        return cls(**tomlkit.loads(open(filename)))

    def write(self, filename):
        tomlkit.dump(self.asdict(), open(filename, 'w'))
