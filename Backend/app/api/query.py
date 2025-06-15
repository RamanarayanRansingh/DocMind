import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.query import SQLQueryHistory
from app.schemas.query import QueryCreate, QueryResponse, QueryHistory as QueryHistorySchema
from app.services.nl_to_sql import NLToSQLService
from ..services.auth import AuthService
from app.models.user import User
from ..utils.logger import log_info, log_error, log_api_request

router = APIRouter(prefix="/query", tags=["query"])
nl_to_sql_service = NLToSQLService()

@router.post("/", response_model=QueryResponse)
async def query_database(
    query: QueryCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        log_api_request("POST", "/query", current_user.id)
        
        # Unpack all three return values: SQL query, results, and natural response
        sql_query, results, natural_response = nl_to_sql_service.generate_sql_query(query.natural_query)
        
        # Save to history (you can store the results as a string, or change your model/schema to store JSON)
        query_history = SQLQueryHistory(
            user_id=current_user.id,
            natural_query=query.natural_query,
            sql_query=sql_query,
            response=natural_response,  # or json.dumps(results) if you prefer
            results=json.dumps(results)
        )
        db.add(query_history)
        db.commit()
        db.refresh(query_history)
        
        log_info(f"Database query processed for user {current_user.id}")
        
        return QueryResponse(
            natural_query=query.natural_query,
            sql_query=sql_query,
            results=results,              
            response=natural_response
        )
    except Exception as e:
        log_error(e, f"Error processing database query for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[QueryHistorySchema])
async def get_query_history(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        log_api_request("GET", "/query/history", current_user.id)
        
        queries = db.query(SQLQueryHistory)\
            .filter(SQLQueryHistory.user_id == current_user.id)\
            .order_by(SQLQueryHistory.timestamp.asc())\
            .all()
        
        for query in queries:
            if query.results:
                query.results = json.loads(query.results)  # Convert from JSON string to list

        log_info(f"Retrieved {len(queries)} query history entries for user {current_user.id}")
        
        return queries
    except Exception as e:
        log_error(e, f"Error retrieving query history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history")
async def clear_query_history(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        log_api_request("DELETE", "/query/history", current_user.id)
        
        deleted_count = db.query(SQLQueryHistory)\
            .filter(SQLQueryHistory.user_id == current_user.id)\
            .delete()
        db.commit()
        
        log_info(f"Cleared {deleted_count} query history entries for user {current_user.id}")
        
        return {"message": "Query history cleared successfully"}
    except Exception as e:
        log_error(e, f"Error clearing query history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))