from typing import List

from models.coordinates import Coordinates


class PathEntry:
    def __init__(self, path_id: str, route: str, path_points: List[Coordinates]) -> None:
        self.path_id = path_id
        self.route = route
        self.path_points = path_points