from typing import List

import asyncpg
from shapely import wkb

import config
from models.coordinates import Coordinates
from models.path import Path


def linestring_to_coords(linestring: str) -> List[Coordinates]:
    parsed = wkb.loads(linestring, hex=True)
    return [Coordinates(lat, lon) for lon, lat in zip(parsed.xy[0], parsed.xy[1])]


async def nearby_routes(lat: float, lon: float, radius: float) -> List[Path]:
    conn = await asyncpg.connect(config.connection_string)

    query = f"""
        select *
        from (select st_distance(st_closestpoint(st_transform(st_setsrid(p.path_geometry, 4326)::geometry, 3857),
                                                 st_transform(ST_SetSRID(st_makepoint({lon}, {lat}), 4326)::geometry,
                                                              3857)),
                                 st_transform(ST_SetSRID(st_makepoint({lon}, {lat}), 4326)::geometry, 3857)) as cp,
                     p.id,
                     p.route_id,
                     p.direction,
                     r.number,
                     r.type,
                     p.path_geometry
                 from route_path p
                       join route r on p.route_id = r.id
              where r.type in ('bus', 'trolleybus', 'tram')
              order by cp asc) as q
        where q.cp < {radius}"""

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
