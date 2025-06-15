from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, validator, Field
from ..database import get_db
from ..services.web_rag import WebRAGService
from ..services.auth import AuthService
from ..models.user import User
from ..models.chat import WebChatHistory  # New model for web chat history
from ..schemas.chat import WebChatMessage, WebChatMessageCreate
from ..utils.logger import log_info, log_error, log_api_request, log_warning
from datetime import datetime
from sqlalchemy import desc
import validators

# Initialize WebRAG service
web_rag_service = WebRAGService()

# Pydantic models
class URLItem(BaseModel):
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        # Allow URLs without protocol for user convenience
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        # Validate the URL
        if not validators.url(v):
            raise ValueError('Invalid URL format')
        return v

class MultipleURLs(BaseModel):
    urls: List[str]
    
    @validator('urls', each_item=True)
    def validate_urls(cls, v):
        # Allow URLs without protocol for user convenience
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
        
        # Validate the URL
        if not validators.url(v):
            raise ValueError(f'Invalid URL format: {v}')
        return v

class WebQueryRequest(BaseModel):
    message: str = Field(..., description="The query/message to ask about the indexed web content")

# Router
router = APIRouter(prefix="/webrag", tags=["webrag"])

@router.post("/url")
async def add_url(
    url_item: URLItem,
    current_user: User = Depends(AuthService.get_current_user),
):
    """Add a URL to the user's WebRAG collection"""
    try:
        log_api_request("POST", "/webrag/url", current_user.id)
        
        result = web_rag_service.add_url_to_collection(current_user.id, url_item.url)
        
        if not result["success"]:
            log_warning(f"Failed to add URL {url_item.url} for user {current_user.id}: {result.get('error', 'Unknown error')}")
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to process URL"))
        
        log_info(f"Added URL {url_item.url} for user {current_user.id}")
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        log_error(e, f"Error adding URL for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/urls")
async def add_multiple_urls(
    urls: MultipleURLs,
    current_user: User = Depends(AuthService.get_current_user),
):
    """Add multiple URLs to the user's WebRAG collection"""
    try:
        log_api_request("POST", "/webrag/urls", current_user.id)
        
        results = web_rag_service.add_multiple_urls(current_user.id, urls.urls)
        
        # Check if any URLs failed to process
        failed_urls = [result for result in results if not result["success"]]
        if failed_urls:
            log_warning(f"Some URLs failed to process for user {current_user.id}: {failed_urls}")
        
        log_info(f"Processed {len(urls.urls)} URLs for user {current_user.id}")
        return {"results": results}
        
    except Exception as e:
        log_error(e, f"Error adding multiple URLs for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/urls")
async def get_indexed_urls(
    current_user: User = Depends(AuthService.get_current_user),
):
    """Get all indexed URLs for the current user"""
    try:
        log_api_request("GET", "/webrag/urls", current_user.id)
        
        urls = web_rag_service.get_indexed_urls(current_user.id)
        
        log_info(f"Retrieved {len(urls)} indexed URLs for user {current_user.id}")
        return {"urls": urls}
        
    except Exception as e:
        log_error(e, f"Error retrieving indexed URLs for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/url")
async def remove_url(
    url_item: URLItem,
    current_user: User = Depends(AuthService.get_current_user),
):
    """Remove a URL from the user's WebRAG collection"""
    try:
        log_api_request("DELETE", "/webrag/url", current_user.id)
        
        result = web_rag_service.remove_url(current_user.id, url_item.url)
        
        if not result["success"]:
            log_warning(f"Failed to remove URL {url_item.url} for user {current_user.id}: {result.get('error', result.get('message', 'Unknown error'))}")
            raise HTTPException(status_code=404, detail=result.get("message", "URL not found"))
        
        log_info(f"Removed URL {url_item.url} for user {current_user.id}")
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        log_error(e, f"Error removing URL for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/urls")
async def clear_all_urls(
    current_user: User = Depends(AuthService.get_current_user),
):
    """Clear all URLs from the user's WebRAG collection"""
    try:
        log_api_request("DELETE", "/webrag/urls", current_user.id)
        
        result = web_rag_service.clear_all_urls(current_user.id)
        
        if not result["success"]:
            log_warning(f"Failed to clear URLs for user {current_user.id}: {result.get('error', result.get('message', 'Unknown error'))}")
            if "No indexed URLs found" in result.get("message", ""):
                return {"message": "No indexed URLs to clear"}
            raise HTTPException(status_code=400, detail=result.get("message", "Failed to clear URLs"))
        
        log_info(f"Cleared all URLs for user {current_user.id}")
        return result
        
    except HTTPException as he:
        raise he
    except Exception as e:
        log_error(e, f"Error clearing URLs for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

# NEW: Chat functionality for WebRAG (consistent with document chat)
@router.post("/chat", response_model=WebChatMessage)
async def create_web_chat_message(
    message: WebChatMessageCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Chat with indexed web content"""
    try:
        log_api_request("POST", "/webrag/chat", current_user.id)
        
        # Get recent chat history for context
        chat_history = (
            db.query(WebChatHistory)
            .filter(WebChatHistory.user_id == current_user.id)
            .order_by(desc(WebChatHistory.timestamp))
            .limit(10)  # Last 10 exchanges
            .all()  
        )
        
        # Format chat history for RAG (reverse to get chronological order)
        formatted_history = [
            (chat.message, chat.response) for chat in reversed(chat_history)
        ]
        
        # Get response from WebRAG
        response = web_rag_service.get_response(
            user_id=current_user.id,
            query=message.message,
            chat_history=formatted_history
        )
        
        # Get sources for reference
        sources = web_rag_service.get_sources_for_query(current_user.id, message.message)
        
        # Save to database
        chat_message = WebChatHistory(
            user_id=current_user.id,
            message=message.message,
            response=response,
            sources=sources,  # Store as JSON
            timestamp=datetime.utcnow()
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        
        log_info(f"Web chat message created for user {current_user.id}")
        
        return WebChatMessage(
            id=chat_message.id,
            user_id=chat_message.user_id,
            message=chat_message.message,
            response=chat_message.response,
            sources=chat_message.sources,
            timestamp=chat_message.timestamp
        )
        
    except Exception as e:
        db.rollback()
        log_error(e, f"Error creating web chat message for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/chat/history", response_model=List[WebChatMessage])
async def get_web_chat_history(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Get web chat history with pagination"""
    try:
        log_api_request("GET", "/webrag/chat/history", current_user.id)
        
        chat_history = (
            db.query(WebChatHistory)
            .filter(WebChatHistory.user_id == current_user.id)
            .order_by(desc(WebChatHistory.timestamp))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        log_info(f"Retrieved web chat history for user {current_user.id}")
        return chat_history
    except Exception as e:
        log_error(e, f"Error fetching web chat history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/chat/history")
async def clear_web_chat_history(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all web chat history for the current user"""
    try:
        log_api_request("DELETE", "/webrag/chat/history", current_user.id)
        
        deleted_count = (
            db.query(WebChatHistory)
            .filter(WebChatHistory.user_id == current_user.id)
            .delete(synchronize_session=False)
        )
        db.commit()
        
        log_info(f"Cleared web chat history for user {current_user.id}")
        
        return {"message": f"Successfully deleted {deleted_count} web chat messages"}
    except Exception as e:
        db.rollback()
        log_error(e, f"Error clearing web chat history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))