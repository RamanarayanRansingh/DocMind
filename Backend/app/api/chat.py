from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from ..database import get_db
from ..models.chat import ChatHistory
from ..schemas.chat import ChatMessage, ChatMessageCreate, ChatHistoryResponse
from ..services.rag import RAGService
from ..services.auth import AuthService
from ..models.user import User
from datetime import datetime
from sqlalchemy import desc
from ..utils.logger import log_info, log_error, log_api_request, log_warning

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize RAG service
rag_service = RAGService()

@router.post("/", response_model=ChatMessage)
async def create_chat_message(
    message: ChatMessageCreate,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    try:
        log_api_request("POST", "/chat", current_user.id)
        
        # Get recent chat history for context
        chat_history = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.user_id == current_user.id,
                ChatHistory.document_id == message.document_id
            )
            .order_by(desc(ChatHistory.timestamp))
            .all()  
        )
        
        # Format chat history for RAG
        formatted_history = [
            (chat.message, chat.response) for chat in reversed(chat_history)
        ]
        
        # Get response from RAG
        response = rag_service.get_response(
            document_id=message.document_id,
            query=message.message,
            #chat_history=formatted_history
        )
        
        # Save to database
        chat_message = ChatHistory(
            user_id=current_user.id,
            document_id=message.document_id,
            message=message.message,
            response=response,
            timestamp=datetime.utcnow()
        )
        db.add(chat_message)
        db.commit()
        db.refresh(chat_message)
        
        log_info(f"Chat message created for user {current_user.id} on document {message.document_id}")
        
        return ChatMessage(
            id=chat_message.id,
            user_id=chat_message.user_id,
            document_id=chat_message.document_id,
            message=chat_message.message,
            response=chat_message.response,
            timestamp=chat_message.timestamp
        )
        
    except Exception as e:
        db.rollback()
        log_error(e, f"Error creating chat message for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{document_id}", response_model=List[ChatMessage])
async def get_document_chat_history(
    document_id: int,
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for a specific document with pagination"""
    try:
        log_api_request("GET", f"/chat/history/{document_id}", current_user.id)
        
        chat_history = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.user_id == current_user.id,
                ChatHistory.document_id == document_id
            )
            .order_by(desc(ChatHistory.timestamp))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        log_info(f"Retrieved chat history for document {document_id}")
        return chat_history
    except Exception as e:
        log_error(e, f"Error fetching document chat history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=List[ChatHistoryResponse])
async def get_all_chat_history(
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
    document_id: Optional[int] = None,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Get all chat history with optional filtering and pagination"""
    try:
        log_api_request("GET", "/chat/history", current_user.id)
        
        query = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id)
        
        if document_id is not None:
            query = query.filter(ChatHistory.document_id == document_id)
        
        total_count = query.count()
        
        chat_history = (
            query
            .order_by(desc(ChatHistory.timestamp))
            .offset(offset)
            .limit(limit)
            .all()
        )
        
        log_info(f"Retrieved {len(chat_history)} chat history entries for user {current_user.id}")
        
        return [
            ChatHistoryResponse(
                id=chat.id,
                user_id=chat.user_id,
                document_id=chat.document_id,
                message=chat.message,
                response=chat.response,
                timestamp=chat.timestamp
            )
            for chat in chat_history
        ]
    except Exception as e:
        log_error(e, f"Error fetching all chat history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history/{document_id}")
async def clear_document_chat_history(
    document_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Clear chat history for a specific document"""
    try:
        log_api_request("DELETE", f"/chat/history/{document_id}", current_user.id)
        
        deleted_count = (
            db.query(ChatHistory)
            .filter(
                ChatHistory.user_id == current_user.id,
                ChatHistory.document_id == document_id
            )
            .delete(synchronize_session=False)
        )
        db.commit()
        
        log_info(f"Cleared chat history for document {document_id} for user {current_user.id}")
        
        return {"message": f"Successfully deleted {deleted_count} chat messages"}
    except Exception as e:
        db.rollback()
        log_error(e, f"Error clearing document chat history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/history")
async def clear_all_chat_history(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all chat history for the current user"""
    try:
        log_api_request("DELETE", "/chat/history", current_user.id)
        
        deleted_count = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == current_user.id)
            .delete(synchronize_session=False)
        )
        db.commit()
        
        log_info(f"Cleared all chat history for user {current_user.id}")
        
        return {"message": f"Successfully deleted {deleted_count} chat messages"}
    except Exception as e:
        db.rollback()
        log_error(e, f"Error clearing all chat history for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))