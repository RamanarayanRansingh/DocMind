import os
import requests
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def register_user(user_data: dict):
    return requests.post(
        f"{BACKEND_URL}/api/register",
        json=user_data
    )

def login_user(email: str, password: str):
    return requests.post(
        f"{BACKEND_URL}/api/login",
        data={"username": email, "password": password}
    )

def get_current_user_profile(token: str):
    return requests.get(
        f"{BACKEND_URL}/api/profile",
        headers={"Authorization": f"Bearer {token}"}
    )


# Add these to your existing api.py
def upload_document(file, token: str):
    return requests.post(
        f"{BACKEND_URL}/documents/upload",
        files={"file": file},
        headers={"Authorization": f"Bearer {token}"}
    )

def get_user_documents(token: str):
    return requests.get(
        f"{BACKEND_URL}/documents/",
        headers={"Authorization": f"Bearer {token}"}
    )

def delete_document(document_id: int, token: str):
    return requests.delete(
        f"{BACKEND_URL}/documents/{document_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

# Add these to your existing api.py
def send_chat_message(document_id: int, message: str, token: str):
    return requests.post(
        f"{BACKEND_URL}/chat/",
        json={"document_id": document_id, "message": message},
        headers={"Authorization": f"Bearer {token}"}
    )

def get_chat_history(document_id: int, token: str):
    return requests.get(
        f"{BACKEND_URL}/chat/history/{document_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

def clear_chat_history(document_id: int, token: str):
    return requests.delete(
        f"{BACKEND_URL}/chat/history/{document_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

def send_nl_query(query: str, token: str):
    return requests.post(
        f"{BACKEND_URL}/query",
        json={"natural_query": query},
        headers={"Authorization": f"Bearer {token}"}
    )

def get_query_history(token: str):
    return requests.get(
        f"{BACKEND_URL}/query/history",
        headers={"Authorization": f"Bearer {token}"}
    )

def clear_query_history(token: str):
    return requests.delete(
        f"{BACKEND_URL}/query/history",
        headers={"Authorization": f"Bearer {token}"}
    )

# WebRAG Functions
def add_url_to_webrag(url: str, token: str):
    return requests.post(
        f"{BACKEND_URL}/webrag/url",
        json={"url": url},
        headers={"Authorization": f"Bearer {token}"}
    )

def add_multiple_urls_to_webrag(urls: list, token: str):
    return requests.post(
        f"{BACKEND_URL}/webrag/urls",
        json={"urls": urls},
        headers={"Authorization": f"Bearer {token}"}
    )

def get_indexed_urls(token: str):
    return requests.get(
        f"{BACKEND_URL}/webrag/urls",
        headers={"Authorization": f"Bearer {token}"}
    )

def remove_url_from_webrag(url: str, token: str):
    return requests.delete(
        f"{BACKEND_URL}/webrag/url",
        json={"url": url},
        headers={"Authorization": f"Bearer {token}"}
    )

def clear_all_webrag_urls(token: str):
    return requests.delete(
        f"{BACKEND_URL}/webrag/urls",
        headers={"Authorization": f"Bearer {token}"}
    )

def send_web_chat_message(message: str, token: str):
    return requests.post(
        f"{BACKEND_URL}/webrag/chat",
        json={"message": message},
        headers={"Authorization": f"Bearer {token}"}
    )

def get_web_chat_history(token: str, limit: int = 50, offset: int = 0):
    return requests.get(
        f"{BACKEND_URL}/webrag/chat/history",
        params={"limit": limit, "offset": offset},
        headers={"Authorization": f"Bearer {token}"}
    )

def clear_web_chat_history(token: str):
    return requests.delete(
        f"{BACKEND_URL}/webrag/chat/history",
        headers={"Authorization": f"Bearer {token}"}
    )