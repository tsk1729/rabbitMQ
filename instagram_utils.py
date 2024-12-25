import requests
from fastapi import HTTPException

from config import SEND_MESSAGE, REPLY_TO_COMMENT


async def send_message(sender_id: str, recipient_id: str, text: str, access_token: str):
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(SEND_MESSAGE.format(sender_id=sender_id), json=payload, headers=headers)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))


async def reply_to_comment(comment_id: str, message: str, access_token: str):
    url = REPLY_TO_COMMENT.format(comment_id=comment_id)
    payload = {"message": message}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return {"status": "success", "response": response.json()}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
