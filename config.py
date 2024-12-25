import os


RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "amqp://localhost:5672")  # Default to localhost if not set
QUEUE_NAME = os.getenv("QUEUE_NAME", "webhook_queue")  # Default to 'webhook_queue'
GET_MEDIA_LIST = "https://graph.instagram.com/v21.0/{user_id}/media"
GET_MEDIA_INFO = "https://graph.instagram.com/v21.0/{media_id}"
REPLY_TO_COMMENT = "https://graph.instagram.com/v21.0/{comment_id}/replies"
SEND_MESSAGE = "https://graph.instagram.com/v21.0/{sender_id}/messages"
