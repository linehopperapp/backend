from json import JSONEncoder
from typing import List, Tuple

from models.coordinates import Coordinates


class Stop:
    class Arrival:
        def __init__(self, vehicle_id: int, label: str, time: int):
            self.vehicle_id = vehicle_id
            self.label = label
            self.time = time

    def __init__(self, id: str, location: Coordinates, arrivals: List[Arrival]):
        self.id = id
        self.location = location
        self.arrivals = arrivals


class StopJSONEncoder(JSONEncoder):
    def default(self, obj):
        return {
            'location': {'lat': obj.location.lat, 'lon': obj.location.lon},
            'arrivals': [{'vehicle_id': a.vehicle_id, 'label': a.label, 'time': a.time} for a in obj.arrivals]
        }
