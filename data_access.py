from typing import List

import asyncpg
from shapely import wkb

import config
from models.coordinates import Coordinates
from models.path import Path


async def nearby_routes(lat: float, lon: float):
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
        where q.cp < 1500"""

    rows = await conn.fetch(query)

    def linestring_to_coords(linestring: str) -> List[Coordinates]:
        parsed = \
            wkb.loads(linestring, hex=True)
        return [Coordinates(lat, lon) for lon, lat in zip(parsed.xy[0], parsed.xy[1])]

    return [Path(row['id'], row['number'], linestring_to_coords(row['path_geometry']), '#FF0000') for row in rows]
