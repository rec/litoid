import json
import tomllib


def load(path):
    t = path.read_text()
    if path.suffix == '.toml':
        return tomllib.loads(t)
    if path.suffix == '.json':
        return json.loads(t)
    raise ValueError(str(path))
