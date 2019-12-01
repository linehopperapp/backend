from typing import List

from shapely import wkb

import config
from models.coordinates import Coordinates
from models.path import Path


def linestring_to_coords(linestring: str) -> List[Coordinates]:
    parsed = wkb.loads(linestring, hex=True)
    return [Coordinates(lat, lon) for lon, lat in zip(parsed.xy[0], parsed.xy[1])]


async def nearby_routes(lat: float, lon: float, radius: float, pool) -> List[Path]:
    async with pool.acquire() as conn:
        query = f"""
            select rp.id, r.number, rp.path_geometry
            from (select min(st_distance(st_transform(st_setsrid(s.geopoint, 4326)::geometry, 3857),
                                         st_transform(ST_SetSRID(st_makepoint({lon}, {lat}), 4326)::geometry, 3857))) as d,
                         s.id
                  from stop s
                  group by s.id) as q
                     join path_stop ps on q.id = ps.stop_id
                     join route_path rp on ps.route_path_id = rp.id
                     join route r on rp.route_id = r.id
            where q.d < {radius} and r.type in ('bus', 'trolleybus', 'tram')"""

        rows = await conn.fetch(query)

        colors = dict()
        last_color = 0

        def get_color(route):
            if route in colors:
                return colors[route]
            else:
                nonlocal last_color
                colors[route] = config.colors[last_color]
                last_color = (last_color + 1) % len(config.colors)
                return colors[route]

        return [Path(row['id'], row['number'], linestring_to_coords(row['path_geometry']), get_color(row['number'])) for row in rows]


async def route_and_path_points(path_id: str, pool) -> (str, List[Coordinates]):
    async with pool.acquire() as conn:
        query = f"select rp.path_geometry, r.number from route_path rp join route r on rp.route_id = r.id where rp.id = '{path_id}'"
        row = await conn.fetchrow(query)
        return (row['route'], linestring_to_coords(row['path_geometry']))