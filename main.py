import asyncio
import logging
from aio_pika import IncomingMessage
from fastapi import FastAPI, HTTPException
import json
import threading
import time

from RabbitMQ import RabbitMQSingleton
from app_logger import logger
from config import RABBITMQ_HOST, QUEUE_NAME
from dto import CommentDTO
from instagram_utils import send_message, reply_to_comment
from mongo import repo_manager

app = FastAPI()


rabbitmq_instance = RabbitMQSingleton(RABBITMQ_HOST, QUEUE_NAME)

def process(message):
    """Process the message with a time delay."""
    logger.info(f"Processing message: {message}")
    time.sleep(4)  # Simulate a delay in processing the message
    logger.info(f"Finished processing message: {message}")


def callback(ch, method, properties, body):
    try:
        # Decode and load the message
        message = json.loads(body)
        logger.info(f"Received message: {message} at time: {time.time()}")
        process(message)  # Call the process function to handle the message
        ch.basic_ack(delivery_tag=method.delivery_tag)  # Acknowledge the message
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)  # Requeue message on error


async def process_message(message):
    logger.debug(f"Processing incoming message: {message}")
    message = CommentDTO(**message)
    subscriber = await repo_manager.paid_subscribers.read({"profile_id": message.post_owner_id})
    if subscriber:
        logger.info(f"Found subscriber: {subscriber['_id']}")
        user_id = subscriber["_id"]
        webhook = await repo_manager.webhooks.find_one(
            {"_id": user_id, "posts.post_id": message.post_id},
            {"posts.$": 1}  # Projection to include only the matching array element
        )
        if webhook:
            logger.info(f"Webhook found for post_id: {message.post_id}")
            sub_string = webhook['sub_string']
            if sub_string in message.text_message:
                logger.info(f"Substring found in message: {sub_string}")
                reply_comment = webhook['bot_message']
                reply_message = webhook['bot_message']
                token = subscriber["token"]
                sender_id = message.post_owner_id
                receiver_id = message.post_owner_id
                comment_id = message.comment_id
                await reply_to_comment(comment_id, reply_comment, token)
                await send_message(sender_id, receiver_id, reply_message, token)
                logger.debug(f"Reply sent to comment: {comment_id}")
                time.sleep(1)


async def consume_messages(rabbitmq_singleton: RabbitMQSingleton, process_message_callback):
    channel = rabbitmq_singleton.get_channel()
    queue_name = rabbitmq_singleton.queue_name
    queue = await channel.declare_queue(queue_name, durable=True)
    logger.info(f"Listening for messages in queue: {queue_name}")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    decoded_body = message.body.decode('utf-8')
                    json_body = json.loads(decoded_body)
                    logger.debug(f"Message received: {json_body}")
                    await process_message_callback(json_body)
                except json.JSONDecodeError:
                    logger.error(f"Error decoding JSON from message: {message.body}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")


@app.on_event("startup")
async def on_startup():
    logger.info("Starting the application...")
    await rabbitmq_instance.setup()
    asyncio.create_task(consume_messages(rabbitmq_instance, process_message))


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down the application...")
    await rabbitmq_instance.close()


if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
