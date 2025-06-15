# backend/app/schemas/query.py

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional

class QueryCreate(BaseModel):
    natural_query: str

class QueryResponse(BaseModel):
    natural_query: str
    sql_query: str
    results: List[dict]
    response: str

class QueryHistory(BaseModel):
    id: int
    user_id: int
    natural_query: str
    sql_query: str
    response: str
    results: Optional[List[dict]]
    timestamp: datetime

    class Config:
       from_attributes = True