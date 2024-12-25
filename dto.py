from pydantic import BaseModel


class CommentDTO(BaseModel):
    person_who_commented_id: str
    username: str
    comment_id: str
    text_message: str
    post_owner_id: str
    post_id:str