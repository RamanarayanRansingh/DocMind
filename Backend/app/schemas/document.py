# backend/app/schemas/document.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class DocumentBase(BaseModel):
    file_name: str
    file_type: str

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: int
    user_id: int
    file_path: str
    uploaded_at: Optional[datetime] = None

    class Config:
        from_attributes = True