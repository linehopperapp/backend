from datetime import time, datetime
from functools import partial
from typing import List

import pyproj
from numpy import mean
from pyproj import transform
from shapely.geometry import LineString, Point

import config
from models.coordinates import Coordinates
from shapely.ops import nearest_points


class VehicleEntry:
    def __init__(self, id: str, path_id: str, route: str, path_points: List[Coordinates]) -> None:
        self.id = id
        self.path_id = path_id
        self.path_points = path_points
        self.path_point_mileages = list(self.get_path_point_mileages(path_points))
        self.route = route
        self.speeds = list()
        self.lat = None
        self.lon = None
        self.mileage = None

    def register_update(self, lat, lon, speed, timestamp):
        self.speeds.append((datetime.fromtimestamp(timestamp), speed * 18 / 5))  # converting km/h to m/s
        self.cleanup_speeds()
        self.lat = lat
        self.lon = lon
        self.mileage = self.get_mileage(lat, lon)

    def cleanup_speeds(self):
        now = datetime.now()
        self.speeds = [(t, speed) for t, speed in self.speeds if (now - t).total_seconds() < config.speed_avg_window]

    def average_speed(self):
        return mean(speed for _, speed in self.speeds)

    def get_mileage(self, lat, lon):
        line = LineString([(pt.lon, pt.lat) for pt in self.path_points])
        point_on_segment = nearest_points(line, Point(lon, lat))[0]
        i, _ = self.nearest_segment(lat, lon)
        return self.path_point_mileages[i] + self.distance(Coordinates(point_on_segment.y, point_on_segment.x), self.path_points[i])
        # todo check point to coordinates transform is correct

    def nearest_segment(self, lat, lon):
        dists = {i: self.distance(Coordinates(lat, lon), pt) for i, pt in enumerate(self.path_points)}

        nearest_idx = min(dists.keys(), key=lambda i: dists[i])
        del dists[nearest_idx]
        second_nearest_idx = min(dists.keys(), key=lambda i: dists[i])

        assert abs(nearest_idx - second_nearest_idx) == 1  # expecting adjacent index

        return (min(nearest_idx, second_nearest_idx), max(nearest_idx, second_nearest_idx))

    @staticmethod
    def get_path_point_mileages(pts: List[Coordinates]):
        d = 0
        yield 0
        for i in range(1, len(pts)):
            d += VehicleEntry.distance(pts[i - 1], pts[i])
            yield d

    @staticmethod
    def distance(pt1: Coordinates, pt2: Coordinates):
        line = LineString([(pt1.lon, pt1.lat), (pt2.lon, pt2.lat)])
        project = partial(
            pyproj.transform,
            pyproj.Proj(init='EPSG:4326'),
            pyproj.Proj(init='EPSG:32633'))
        metric = transform(project, line)
        return metric.length
