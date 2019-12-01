import asyncio
import json
import os
from functools import partial

import asyncpg
from aiohttp import web

import config
from data_access.paths import nearby_routes
from data_access.stops import nearby_stops
from models.path import PathJSONEncoder
from models.stop import StopJSONEncoder


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


async def init_app():
    app = web.Application()

    routes = [
        web.get('/paths', handle_paths),
        web.get('/stops', handle_stops)
    ]

    app.add_routes(routes)

    app['pool'] = await asyncpg.create_pool(dsn=config.connection_string)

    return app


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = loop.run_until_complete(init_app())
    web.run_app(app, port=os.environ['PORT'] if 'PORT' in os.environ else 8080)
