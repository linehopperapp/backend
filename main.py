import asyncio
import json
import os
from datetime import datetime, timedelta
from functools import partial

import asyncpg
from aiohttp import web

import config
from db_access.paths import nearby_routes
from db_access.stops import nearby_stops
from models.path import PathJSONEncoder
from models.stop import StopJSONEncoder
from models.vehicle import Vehicle, VehicleJSONEncoder
from tracking.vehicle_tracker import VehicleTracker


async def handle_paths(request):
    lat = float(request.rel_url.query['lat'])
    lon = float(request.rel_url.query['lon'])

    pool = request.app['pool']
    data = await nearby_routes(lat, lon, config.radius, pool)

    return web.json_response(data, dumps=partial(json.dumps, cls=PathJSONEncoder))


async def handle_stops(request):
    lat = float(request.rel_url.query['lat'])
    lon = float(request.rel_url.query['lon'])
    radius = float(request.rel_url.query['radius']) if 'radius' in request.rel_url.query else config.radius

    pool = request.app['pool']
    stops = await nearby_stops(lat, lon, radius, pool)

    return web.json_response(stops, dumps=partial(json.dumps, cls=StopJSONEncoder))


async def handle_vehicles(request):
    if not request.can_read_body:
        return web.HTTPBadRequest()

    body = await request.json()
    # for path_id in body:
    #     pass

    data = [Vehicle('1', '89f5ac8e-efa2-49e0-8014-6d56b543b9c5',
                    [Vehicle.Target(1000, datetime.now() + timedelta(seconds=60)),
                     Vehicle.Target(2000, datetime.now() + timedelta(seconds=120))])]

    return web.json_response(data, dumps=partial(json.dumps, cls=VehicleJSONEncoder))



async def init_app():
    app = web.Application()

    routes = [
        web.get('/paths', handle_paths),
        web.get('/stops', handle_stops),
        web.post('/vehicles', handle_vehicles)
    ]

    app.add_routes(routes)

    app['pool'] = await asyncpg.create_pool(dsn=config.pg_connection_string)

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    #tracker = VehicleTracker(loop)
    app = loop.run_until_complete(init_app())
    web.run_app(app, port=os.environ['PORT'] if 'PORT' in os.environ else 8080)
