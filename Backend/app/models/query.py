from typing import List, Optional
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..database import Base

class SQLQueryHistory(Base):
    __tablename__ = "sql_query_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    natural_query= Column(Text, nullable=False)
    sql_query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    results = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="query_history")
