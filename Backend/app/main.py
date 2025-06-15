from fastapi import FastAPI
from app.database import engine, Base
from app.utils.logger import log_info
from .api import auth, query, chat, documents, web_chat

# Create database tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(title="RAG-based Query System", version="1.0")

# Include routers
app.include_router(auth.router)
app.include_router(query.router)
app.include_router(chat.router)
app.include_router(documents.router)
app.include_router(web_chat.router)

@app.get("/")
def root():
    log_info("Root endpoint accessed")
    return {"message": "Welcome to the RAG-based Query System!"}
