import json
import tomlkit
import tomllib


def load(path):
    t = path.read_text()
    if path.suffix == '.toml':
        return tomllib.loads(t)
    if path.suffix == '.json':
        return json.loads(t)
    raise ValueError(str(path))


def dump(path, value):
    if path.suffix == '.toml':
        s = tomlkit.dumps(value)
    elif path.suffix == '.json':
        s = json.dumps(value, indent=2)
    else:
        raise ValueError(str(path))
    path.write_text(s)
