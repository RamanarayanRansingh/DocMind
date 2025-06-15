from fastapi import UploadFile, HTTPException
from pathlib import Path
import os
import shutil
from typing import List
from sqlalchemy.orm import Session
from ..models.document import Document
from ..schemas.document import DocumentCreate
import magic  # for file type detection

class DocumentService:
    ALLOWED_EXTENSIONS = {
        'pdf': 'application/pdf',
        'csv': 'text/csv',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'xls': 'application/vnd.ms-excel'
    }
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
    
    async def save_file(self, file: UploadFile, user_id: int) -> str:
        """Save uploaded file to disk and return the file path"""
        content_type = magic.from_buffer(await file.read(1024), mime=True)
        await file.seek(0)  # Reset file pointer
        
        if content_type not in self.ALLOWED_EXTENSIONS.values():
            raise HTTPException(status_code=400, detail="File type not allowed")
        
        user_upload_dir = self.upload_dir / str(user_id)
        user_upload_dir.mkdir(exist_ok=True)
        
        file_path = user_upload_dir / file.filename
        
        try:
            with file_path.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
            
        return str(file_path)
    
    def create_document(self, db: Session, user_id: int, file_path: str, 
                       file_name: str, file_type: str) -> Document:
        """Create document record in database"""
        db_document = Document(
            user_id=user_id,
            file_name=file_name,
            file_type=file_type,
            file_path=file_path
        )
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        return db_document
    
    def get_user_documents(self, db: Session, user_id: int) -> List[Document]:
        """Get all documents for a user"""
        return db.query(Document).filter(Document.user_id == user_id).all()
    
    def get_document(self, db: Session, document_id: int, user_id: int) -> Document:
        """Get specific document ensuring it belongs to the user"""
        document = db.query(Document).filter(
            Document.id == document_id,
            Document.user_id == user_id
        ).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return document
    
    def delete_document(self, db: Session, document_id: int, user_id: int) -> bool:
        """Delete document from database and filesystem"""
        document = self.get_document(db, document_id, user_id)
        
        # Delete file from filesystem
        try:
            os.remove(document.file_path)
        except OSError:
            pass  # File might not exist
        
        # Delete from database
        db.delete(document)
        db.commit()
        return True