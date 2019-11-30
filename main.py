import json
import os
from functools import partial

from aiohttp import web

from data_access import nearby_routes
from models.coordinates import Coordinates
from models.path import Path, PathJSONEncoder
from models.stop import Stop, StopJSONEncoder


async def handle_paths(request):
    lat = float(request.rel_url.query['lat'])
    lon = float(request.rel_url.query['lon'])
    data = await nearby_routes(lat, lon)

    #data = [Path('path1', '1', [Coordinates(60, 30), Coordinates(60.1, 30.1)], '#00FF00'),
    #        Path('path2', '2', [Coordinates(60, 30), Coordinates(59.9, 30.1)], '#FF0000')]

    return web.json_response(data, dumps=partial(json.dumps, cls=PathJSONEncoder))


async def handle_stops(request):
    mock = [Stop(Coordinates(60, 30), [Stop.Arrival(1, '12', 5), Stop.Arrival(2, '21', 7)]),
            Stop(Coordinates(60.1, 30.1), [Stop.Arrival(1, '13', 5), Stop.Arrival(2, '22', 7)])]
    return web.json_response(mock, dumps=partial(json.dumps, cls=StopJSONEncoder))


app = web.Application()

routes = [
    web.get('/paths', handle_paths),
    web.get('/stops', handle_stops)
]

app.add_routes(routes)

web.run_app(app, port=os.environ['PORT'] if 'PORT' in os.environ else 8080)
