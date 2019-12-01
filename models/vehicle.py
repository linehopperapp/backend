from json import JSONEncoder
from typing import List

from models.coordinates import Coordinates


class Vehicle:
    class Target:
        def __init__(self, progress: float, time: float) -> None:
            self.progress = progress
            self.time = time

    def __init__(self, id: str, path_id: str, targets: List[Target]) -> None:
        self.id = id,
        self.path_id = path_id,
        self.targets = targets


class VehicleJSONEncoder(JSONEncoder):
    def default(self, o):
        return {
            'id': o.id,
            'path_id': o.path_id,
            'targets': [{
                'progress': t.progress,
                'time': t.time.timestamp()
            } for t in o.targets]
        }
