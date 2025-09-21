import json, pathlib

DATA = pathlib.Path(__file__).parent.parent / "data"

def _read_json(path: pathlib.Path):
    return json.loads(path.read_text(encoding="utf-8"))

def load_people():
    return _read_json(DATA / "people.json")

def load_tasks():
    return _read_json(DATA / "tasks.json")

def load_slack_digest():
    return _read_json(DATA / "slack_digest.json")

def load_github():
    return _read_json(DATA / "github_mock.json")
