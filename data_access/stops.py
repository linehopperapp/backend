import asyncpg
from typing import List
import config
from models.coordinates import Coordinates
from models.stop import Stop


async def nearby_stop_ids(lat: float, lon: float, radius: float) -> List[str]:
    conn = await asyncpg.connect(config.connection_string)

    query = f"""select id
                from (select st_distance(st_transform(st_setsrid(s.geopoint, 4326)::geometry, 3857),
                                         st_transform(ST_SetSRID(st_makepoint({lon}, {lat}), 4326)::geometry, 3857)) as d,
                             id
                      from stop s
                      order by d asc) as q
                where q.d < {radius}"""

    rows = await conn.fetch(query)

    return [r['id'] for r in rows]


async def all_stops(lat: float, lon: float) -> List[Stop]:
    conn = await asyncpg.connect(config.connection_string)

    query = f"""
                select distinct s.id, s.lat, s.lon
                from (select min(st_distance(st_transform(st_setsrid(s.geopoint, 4326)::geometry, 3857),
                                             st_transform(ST_SetSRID(st_makepoint({lon}, {lat}), 4326)::geometry, 3857))) as d,
                             ps.route_path_id
                      from stop s
                               join path_stop ps on s.id = ps.stop_id
                               join route_path rp on ps.route_path_id = rp.id
                      group by ps.route_path_id) as q
                         join path_stop ps on q.route_path_id = ps.route_path_id
                         join stop s on s.id = ps.stop_id
                where q.d < 1500;
                """

    rows = await conn.fetch(query)

    return [Stop(r['id'], Coordinates(float(r['lat']), float(r['lon'])), arrivals=[]) for r in rows]
