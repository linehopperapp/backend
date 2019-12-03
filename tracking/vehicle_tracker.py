import json
from datetime import datetime

from aio_pika import connect, ExchangeType, IncomingMessage

import config
from db_access.paths import route_and_path_points
from models.vehicle import Vehicle
from tracking.path_entry import PathEntry
from tracking.vehicle_entry import VehicleEntry


class VehicleTracker:
    def __init__(self, loop, pool) -> None:
        loop.create_task(self.__listen(loop))
        self.vehicles = dict()
        self.paths = dict()
        self.pool = pool

    async def __listen(self, loop):
        connection = await connect(config.amqp_connection_string, loop=loop)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        exchange = await channel.declare_exchange(config.amqp_exchange, ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange, routing_key=config.amqp_routing_key)
        await queue.consume(self.__process_message)

    def __process_message(self, message: IncomingMessage):
        with message.process():
            parsed = json.loads(message.body)
            self.__vehicle_update(parsed['transportId'], parsed['lat'], parsed['lon'], parsed['speed'], parsed['createdAt'], parsed['pathId'])

    def __vehicle_update(self, id: str, lat: float, lon: float, speed: float, timestamp: float, path_id: str) -> None:
        if not id in self.vehicles:
            if not path_id in self.paths:
                route, pts = route_and_path_points(path_id, self.pool)
                self.paths[path_id] = PathEntry(path_id, route, pts)
            self.vehicles[id] = VehicleEntry(id, path_id, self.paths[path_id].route, self.paths[path_id].path_points)
        self.vehicles[id].register_update(lat, lon, speed, timestamp)

    def vehicle_animation(self, id: str, secs: float) -> Vehicle:
        if id in self.vehicles:
            v = self.vehicles[id]
            return Vehicle(id, v.path_id, [Vehicle.Target(v.mileage + v.average_speed * secs, datetime.utcnow().timestamp())])

    def vehicle_forecast(self, id: str):
        pass

    def stop_forecast(self, id: str):
        pass
