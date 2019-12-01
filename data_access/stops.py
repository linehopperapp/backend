import asyncpg
from typing import List
import config
from models.coordinates import Coordinates
from models.stop import Stop


async def nearby_stops(lat: float, lon: float, radius: float, pool) -> List[Stop]:
    async with pool.acquire() as conn:
        query = f"""select q.lat, q.lon
                    from (select (st_distance(st_transform(st_setsrid(s.geopoint, 4326)::geometry, 3857),
                                              st_transform(ST_SetSRID(st_makepoint({lon}, {lat}), 4326)::geometry, 3857))) as d,
                                 s.lat,
                                 s.lon
                          from stop s
                         ) as q
                    where q.d < {radius};
                """

        rows = await conn.fetch(query)

        return [Stop(Coordinates(float(r['lat']), float(r['lon'])), arrivals=[]) for r in rows]