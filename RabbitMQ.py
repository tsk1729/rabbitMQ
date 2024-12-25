import aio_pika
from typing import Optional

from fastapi import HTTPException


class RabbitMQSingleton:
    _instance: Optional["RabbitMQSingleton"] = None

    def __new__(cls, host: str, queue_name: str):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.host = host
            cls._instance.queue_name = queue_name
            cls._instance.connection = None
            cls._instance.channel = None
        return cls._instance

    async def setup(self):
        if self.connection is None or self.channel is None:
            self.connection = await aio_pika.connect_robust(self.host)
            self.channel = await self.connection.channel()  # Create channel asynchronously
            await self.channel.declare_queue(self.queue_name, durable=True)  # Declare queue
        return self.channel

    async def close(self):
        if self.channel:
            await self.channel.close()
        if self.connection:
            await self.connection.close()

    def get_connection(self):
        """Getter for the RabbitMQ connection."""
        if not self.connection:
            raise HTTPException(status_code=500, detail="RabbitMQ connection is not initialized.")
        return self.connection

    def get_channel(self):
        """Getter for the RabbitMQ channel."""
        if not self.channel:
            raise HTTPException(status_code=500, detail="RabbitMQ channel is not initialized.")
        return self.channel