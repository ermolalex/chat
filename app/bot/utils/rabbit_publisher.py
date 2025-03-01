import json
from pika import ConnectionParameters, PlainCredentials, BlockingConnection

from app.config import settings


class RabbitPublisher:
    def __init__(self, exchange="", queue='hello', routing_key='hello'):
        self.exchange = exchange
        self.queue = queue
        self.routing_key = routing_key

        self.credentials = PlainCredentials(settings.RABBIT_USER, settings.RABBIT_USER_PSW)
        self.connection_params = ConnectionParameters(
            host="localhost",  # "89.38.135.232",
            port=5672,
            credentials=credentials,
        )


    def publish(self, msg):
        with BlockingConnection(connection_params) as conn:
            with conn.channel() as ch:
                ch.queue_declare(queue=self.queue)

                ch.basic_publish(
                    exchange=self.exchange,
                    routing_key=self.routing_key,
                    body=json.dumps(msg)
                )

