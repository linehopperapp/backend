from json import JSONEncoder
from typing import List, Tuple

from models.coordinates import Coordinates


class Path:
    def __init__(self, path_id: str, label: str, track: List[Coordinates], color: str):
        self.path_id = path_id
        self.label = label
        self.track = track
        self.color = color


class PathJSONEncoder(JSONEncoder):
    def default(self, obj):
        return {
            'path_id': obj.path_id,
            'label': obj.label,
            'color': obj.color,
            'track': [{'lat': coords.lat, 'lon': coords.lon} for coords in obj.track]
        }
