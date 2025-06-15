from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import os
from ..database import get_db
from ..schemas.document import Document as DocumentSchema
from ..services.document import DocumentService
from ..services.rag import RAGService
from ..services.auth import AuthService
from ..models.user import User
from ..utils.logger import log_info, log_error, log_api_request, log_warning

router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize services
document_service = DocumentService()
rag_service = RAGService()

@router.post("/upload", response_model=DocumentSchema)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a new document and process it for RAG
    """
    try:
        log_api_request("POST", "/documents/upload", current_user.id)
        
        # Get file extension
        file_extension = os.path.splitext(file.filename)[1][1:].lower()
        file_name = os.path.splitext(file.filename)[0].lower()

        # Validate file type
        if file_extension not in ['pdf', 'csv', 'xlsx', 'xls']:
            log_warning(f"Unsupported file type uploaded: {file_extension}")
            raise HTTPException(
                status_code=400,
                detail="File type not supported. Please upload PDF, CSV, or Excel files."
            )
        
        # Save file
        file_path = await document_service.save_file(file, current_user.id)
        log_info(f"File saved at: {file_path}")
        
        # Create document record
        document = document_service.create_document(
            db=db,
            user_id=current_user.id,
            file_path=file_path,
            file_name=file_name,
            file_type=file_extension
        )
        log_info(f"Document created in database with ID: {document.id}")
        
        # Process document for RAG
        try:
            log_info(f"Processing document {document.id} for RAG...")
            rag_service.process_document(
                document_id=document.id,
                file_path=file_path,
                file_type=file_extension
            )
            log_info(f"Document {document.id} processed successfully for RAG.")
        except Exception as e:
            log_error(e, f"Failed to process document {document.id} for RAG")
            # If RAG processing fails, delete the document and raise error
            document_service.delete_document(db, document.id, current_user.id)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process document: {str(e)}"
            )
        
        return document
        
    except Exception as e:
        log_error(e, f"Error uploading document for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get("/", response_model=List[DocumentSchema])
async def get_documents(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all documents for the current user
    """
    try:
        log_api_request("GET", "/documents", current_user.id)
        
        documents = document_service.get_user_documents(db, current_user.id)
        log_info(f"Retrieved {len(documents)} documents for user {current_user.id}")
        
        return documents
    except Exception as e:
        log_error(e, f"Error retrieving documents for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{document_id}", response_model=DocumentSchema)
async def get_document(
    document_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific document
    """
    try:
        log_api_request("GET", f"/documents/{document_id}", current_user.id)
        
        document = document_service.get_document(db, document_id, current_user.id)
        if not document:
            log_warning(f"Document {document_id} not found for user {current_user.id}")
            raise HTTPException(status_code=404, detail="Document not found")
        
        log_info(f"Retrieved document {document_id} for user {current_user.id}")
        return document
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"Error retrieving document {document_id} for user {current_user.id}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a document and its associated RAG data
    """
    try:
        log_api_request("DELETE", f"/documents/{document_id}", current_user.id)
        
        # Get document first to ensure it exists and belongs to user
        document = document_service.get_document(db, document_id, current_user.id)
        if not document:
            log_warning(f"Document {document_id} not found for deletion")
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Clean up RAG data first
        try:
            rag_service.cleanup_document(document_id)
        except Exception as e:
            log_error(e, f"Failed to cleanup RAG data for document {document_id}")
            # Continue with document deletion even if RAG cleanup fails
        
        # Delete the document
        success = document_service.delete_document(db, document_id, current_user.id)
        if not success:
            log_warning(f"Failed to delete document {document_id}")
            raise HTTPException(status_code=500, detail="Failed to delete document")
        
        log_info(f"Document {document_id} deleted successfully")
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        log_error(e, f"Error deleting document {document_id}")
        raise HTTPException(status_code=500, detail="Internal server error")