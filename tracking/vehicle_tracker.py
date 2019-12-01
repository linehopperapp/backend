import asyncio

from aio_pika import connect, ExchangeType, IncomingMessage, message

import config
from models.vehicle import Vehicle


class VehicleTracker:
    def __init__(self, loop) -> None:
        loop.create_task(self.__listen(loop))

    async def __listen(self, loop):
        connection = await connect(config.amqp_connection_string, loop=loop)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)
        exchange = await channel.declare_exchange(config.amqp_exchange, ExchangeType.TOPIC, durable=True)
        queue = await channel.declare_queue(exclusive=True)
        await queue.bind(exchange, routing_key=config.amqp_routing_key)
        await queue.consume(VehicleTracker.__process_message)


    @staticmethod
    def __process_message(message : IncomingMessage):
        print("processing message")
        with message.process():
            print("[x] %r" % message.body)

    async def __vehicle_update(self, id: str, lat: float, lon: float, speed: float, timestamp: float, path: str) -> None:
        pass

    def vehicle_animation(self, id: str, secs: float) -> Vehicle:
        pass

    def vehicle_forecast(self, id: str):
        pass

    def stop_forecast(self, id: str):
        pass
