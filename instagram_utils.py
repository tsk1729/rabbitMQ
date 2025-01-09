import requests
from fastapi import HTTPException

from app_logger import logger
from config import SEND_MESSAGE, REPLY_TO_COMMENT, PRIVATE_REPLY_TO_COMMENT
from urllib.parse import urlparse


async def send_message(sender_id: str, recipient_id: str, text: str, access_token: str):
    logger.info("Inside send_message function")
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        logger.info("Calling send API with headers: {} payload:{} ".format(headers, payload))
        response = requests.post(SEND_MESSAGE.format(sender_id=sender_id), json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"Response received is {response.json()}")
        logger.info(f"Message sent to {recipient_id} from {sender_id} successfully")
        logger.info("Exiting send_message function")
    except requests.exceptions.RequestException as e:
        logger.error(
            f"Unable to send message from recipient {recipient_id} to sender {sender_id} with error message: {e}")
        logger.info("Exiting send_message function")
        raise HTTPException(status_code=400, detail=str(e))


async def reply_to_comment(comment_id: str, message: str, access_token: str):
    logger.info("Inside reply_to_comment function")
    url = REPLY_TO_COMMENT.format(comment_id=comment_id)
    payload = {"message": message}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        logger.info("Calling Reply to Comment API with headers: {}".format(headers))
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"Response received is {response.json()}")
        logger.info("Exiting reply_to_comment function")
    except requests.exceptions.RequestException as e:
        logger.error(f"Unable to reply for comment for comment_id {comment_id} with error message: {e}")
        logger.info("Exiting reply_to_comment function")
        raise HTTPException(status_code=400, detail=str(e))


def is_url(text):
    parsed_url = urlparse(text)
    logger.info("Parsed url:", parsed_url)
    logger.info("Result:", bool(parsed_url.netloc))
    return bool(parsed_url.netloc)


def generate_payload(text, comment_id):
    logger.info("Inside Generate Payload")
    flag = is_url(text)
    if flag:
        payload = {
            "recipient": {
                "id": comment_id
            },
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "generic",
                        "elements": [
                            {
                                "title": "Check out this product!",
                                "subtitle": "Click the button below to view more details.",
                                "image_url": "https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExMDFqZG1wZnd1ZjBndnNzd3MwNnY1NjdhOXdpbWdpeHp1cWx2OG4yMSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/g80laQY3eau4DRrdjF/giphy.gif",
                                "buttons": [
                                    {
                                        "type": "web_url",
                                        "url":text,
                                        "title": "Product link"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        }
    else:
        payload = {
            "recipient": {"comment_id": comment_id},
            "message": {"text": text}
        }
    logger.info(f"Exiting generating payload with {payload}")
    return payload


async def private_message_to_comment(comment_id, message, profile_id, token):
    logger.info("Inside private_message_to_comment function")
    url = PRIVATE_REPLY_TO_COMMENT.replace("{user_id}", profile_id)
    logger.info("url {url}")
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    payload = generate_payload(message, comment_id)
    logger.info("Calling send API with headers: {} payload:{} ".format(headers, payload))
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        logger.info(f"Response received {response.json()}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Unable to send private message for comment_id {comment_id} with error message: {e}")
        logger.info("Exiting private_message_to_comment function")
        raise HTTPException(status_code=500, detail=str(e))
