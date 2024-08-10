from pydantic import BaseModel


class ChatRequest(BaseModel):
    questions: str
    session: str
