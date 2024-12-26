import asyncio
import logging
from aio_pika import IncomingMessage
from fastapi import FastAPI, HTTPException
import json
import time

from RabbitMQ import RabbitMQSingleton
from app_logger import logger
from config import RABBITMQ_HOST, QUEUE_NAME
from dto import CommentDTO
from instagram_utils import send_message, reply_to_comment, private_message_to_comment
from mongo import repo_manager

app = FastAPI()


rabbitmq_instance = RabbitMQSingleton(RABBITMQ_HOST, QUEUE_NAME)


async def process_message(message):
    logger.info(f"Processing incoming message: {message}")
    message = CommentDTO(**message)
    subscriber = await repo_manager.paid_subscribers.read({"profile_id": message.post_owner_id})
    logger.info("Subscriber found: {}".format(subscriber))
    if subscriber:
        logger.info("Subscriber exists")
        user_id = subscriber["_id"]
        webhook = await repo_manager.webhooks.collection.find_one(
            {"_id": user_id, "posts.post_id": message.post_id},
            {"posts.$": 1}
        )
        logger.info("Webhook found: {}".format(webhook))
        if webhook:
            logger.info(f"Webhook found for post_id: {message.post_id} is {webhook}")
            sub_string = webhook['posts'][0]['sub_string']
            if sub_string.lower() in message.text_message.lower():
                logger.info(f"Substring found in message: {sub_string}")
                reply_comment = webhook['posts'][0]['bot_message']
                logger.info("Reply comment: {}".format(reply_comment))
                reply_message = webhook['posts'][0]['bot_message']
                logger.info("Reply message: {}".format(reply_message))
                token = subscriber["token"]
                sender_id = message.post_owner_id
                receiver_id = message.post_owner_id
                comment_id = message.comment_id
                logger.info(f"Calling reply_to_comment function with comment_id , reply_comment and token: {comment_id}, {reply_comment}, {token}")
                await reply_to_comment(comment_id, reply_comment, token)
                logger.info("Ended reply_to_comment function")
                logger.info(
                    f"Calling private_message_to_comment function with parameters comment_id, reply_message, "
                    f"sender_id and token : {comment_id},{reply_message},{sender_id},{token}")
                await private_message_to_comment(comment_id, reply_message,sender_id,token)
                logger.info("Ended private_message_to_comment  function")
                logger.info(f"Reply sent to comment: {comment_id}")
                time.sleep(1)


async def consume_messages(rabbitmq_singleton: RabbitMQSingleton, process_message_callback):
    logger.info("Fetching Channel")
    channel = rabbitmq_singleton.get_channel()
    logger.info(f"Channel found channel {channel}")
    queue_name = rabbitmq_singleton.queue_name
    logger.info("Fetching Queue")
    queue = await channel.declare_queue(queue_name, durable=True)
    logger.info(f"Queue found {queue}")
    logger.info(f"Listening for messages in queue: {queue_name}")
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                try:
                    decoded_body = message.body.decode('utf-8')
                    json_body = json.loads(decoded_body)
                    logger.info(f"Message received: {json_body}")
                    await process_message_callback(json_body)
                except json.JSONDecodeError:
                    logger.error(f"Error decoding JSON from message: {message.body}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")


@app.on_event("startup")
async def on_startup():
    logger.info("Starting the application...")
    await rabbitmq_instance.setup()
    await asyncio.create_task(consume_messages(rabbitmq_instance, process_message))


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Shutting down the application...")
    await rabbitmq_instance.close()


if __name__ == "__main__":
    logger.info("Starting FastAPI application...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
