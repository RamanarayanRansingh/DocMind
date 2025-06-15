# backend/app/schemas/chat.py
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List, Optional

class ChatMessageBase(BaseModel):
    message: str
    document_id: int

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    user_id: int
    response: str
    timestamp: datetime

class ChatHistoryResponse(BaseModel):
    history: List[ChatMessage]

    class Config:
        from_attributes = True


class WebChatMessageCreate(BaseModel):
    message: str

class WebChatMessage(BaseModel):
    id: int
    user_id: int
    message: str
    response: str
    sources: Optional[List[Dict[str, str]]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True

class WebChatHistoryResponse(BaseModel):
    id: int
    user_id: int
    message: str
    response: str
    sources: Optional[List[Dict[str, str]]] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True