from typing import Optional, List, Dict, Union
import requests
from bs4 import BeautifulSoup
import urllib.parse
import logging
import uuid
import hashlib
import os
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from ..config import Settings
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentenceTransformerEmbedding(EmbeddingFunction):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.model = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
        return cls._instance

    def __call__(self, input: Documents) -> Embeddings:
        if not input:
            return []
        return self.model.embed_documents(input)

class WebRAGService:
    def __init__(self, persist_directory: str = "web_chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        self.collection_name_template = "web_{user_id}"
        
        # Initialize components
        self.embedding_function = SentenceTransformerEmbedding()
        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama3-70b-8192",
            groq_api_key=Settings().GROQ_API_KEY,
            max_tokens=1024
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        # Headers to appear more like a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Initialize ChromaDB client
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
            logger.info("WebRAG ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"WebRAG ChromaDB initialization failed: {str(e)}")
            raise

    def _collection_name(self, user_id: int) -> str:
        return self.collection_name_template.format(user_id=user_id)
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract main content text from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script_or_style in soup(['script', 'style', 'nav', 'footer', 'header']):
                script_or_style.decompose()
            
            # Get text
            text = soup.get_text(separator='\n')
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception as e:
            logger.error(f"HTML extraction failed: {str(e)}")
            return ""

    def _calculate_url_hash(self, url: str) -> str:
        """Calculate SHA-256 hash of URL"""
        hash_sha256 = hashlib.sha256()
        hash_sha256.update(url.encode('utf-8'))
        return hash_sha256.hexdigest()
    
    def scrape_url(self, url: str) -> Dict[str, Union[str, bool]]:
        """Scrape content from a URL"""
        try:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Fetch the URL
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Extract text
            text = self._extract_text_from_html(response.text)
            
            # Get page title
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string if soup.title else url
            
            return {
                "success": True,
                "url": url,
                "title": title,
                "text": text,
                "hash": self._calculate_url_hash(url)
            }
        except Exception as e:
            logger.error(f"Failed to scrape URL {url}: {str(e)}")
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    def add_url_to_collection(self, user_id: int, url: str) -> Dict[str, Union[str, bool]]:
        """Add a URL to a user's collection"""
        try:
            # Get the collection name
            collection_name = self._collection_name(user_id)
            
            # Create or get the collection
            try:
                collection = self.chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            except Exception:
                collection = self.chroma_client.create_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            
            # Scrape the URL
            url_data = self.scrape_url(url)
            if not url_data["success"]:
                return url_data
            
            # Check if URL already exists in collection
            url_hash = url_data["hash"]
            existing_items = collection.get(
                where={"url_hash": url_hash},
                include=["metadatas"]
            )
            
            if existing_items["ids"]:
                # URL already exists
                logger.info(f"URL {url} already exists in collection for user {user_id}")
                return {
                    "success": True,
                    "message": "URL already indexed",
                    "url": url,
                    "title": url_data["title"],
                    "is_new": False
                }
            
            # Split the text into chunks
            chunks = self.text_splitter.split_text(url_data["text"])
            
            if not chunks:
                return {
                    "success": False,
                    "url": url,
                    "error": "No content could be extracted from the URL"
                }
            
            # Add chunks to collection
            batch_ids = [str(uuid.uuid4()) for _ in chunks]
            batch_metadata = [{
                "url": url,
                "title": url_data["title"],
                "url_hash": url_hash,
                "chunk_index": i
            } for i in range(len(chunks))]
            
            collection.add(
                documents=chunks,
                ids=batch_ids,
                metadatas=batch_metadata
            )
            
            logger.info(f"Added URL {url} to collection for user {user_id} with {len(chunks)} chunks")
            
            return {
                "success": True,
                "message": "URL indexed successfully",
                "url": url,
                "title": url_data["title"],
                "chunks_count": len(chunks),
                "is_new": True
            }
            
        except Exception as e:
            logger.error(f"Failed to add URL to collection: {str(e)}")
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    def add_multiple_urls(self, user_id: int, urls: List[str]) -> List[Dict[str, Union[str, bool]]]:
        """Add multiple URLs to a user's collection"""
        results = []
        for url in urls:
            result = self.add_url_to_collection(user_id, url)
            results.append(result)
        return results
    
    def get_indexed_urls(self, user_id: int) -> List[Dict[str, str]]:
        """Get a list of all indexed URLs for a user"""
        try:
            collection_name = self._collection_name(user_id)
            
            try:
                collection = self.chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            except Exception:
                logger.info(f"No collection found for user {user_id}")
                return []
            
            # Get all metadatas
            all_items = collection.get(include=["metadatas"])
            
            # Extract unique URLs
            seen_urls = set()
            urls_data = []
            
            for metadata in all_items["metadatas"]:
                url_hash = metadata.get("url_hash")
                url = metadata.get("url")
                title = metadata.get("title")
                
                if url_hash and url_hash not in seen_urls:
                    seen_urls.add(url_hash)
                    urls_data.append({
                        "url": url,
                        "title": title,
                        "url_hash": url_hash
                    })
            
            return urls_data
            
        except Exception as e:
            logger.error(f"Failed to get indexed URLs: {str(e)}")
            return []
    
    def remove_url(self, user_id: int, url: str) -> Dict[str, Union[str, bool]]:
        """Remove a URL from a user's collection"""
        try:
            collection_name = self._collection_name(user_id)
            url_hash = self._calculate_url_hash(url)
            
            try:
                collection = self.chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            except Exception:
                return {
                    "success": False,
                    "message": "No indexed URLs found for this user"
                }
            
            # Get IDs of items with matching URL hash
            # Fix: Use include=["metadatas"] and filter the results
            matching_items = collection.get(
                where={"url_hash": url_hash},
                include=["metadatas"]  # Changed from "ids" to "metadatas"
            )
            
            if not matching_items["ids"]:
                return {
                    "success": False,
                    "message": "URL not found in indexed content"
                }
            
            # Delete all chunks for this URL using the IDs we got
            collection.delete(ids=matching_items["ids"])
            
            logger.info(f"Removed URL {url} from collection for user {user_id}")
            
            return {
                "success": True,
                "message": f"URL {url} removed successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to remove URL: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def clear_all_urls(self, user_id: int) -> Dict[str, Union[str, bool]]:
        """Clear all indexed URLs for a user"""
        try:
            collection_name = self._collection_name(user_id)
            
            try:
                self.chroma_client.delete_collection(collection_name)
                logger.info(f"Deleted collection for user {user_id}")
                
                return {
                    "success": True,
                    "message": "All indexed URLs have been cleared"
                }
            except Exception:
                return {
                    "success": False,
                    "message": "No indexed URLs found for this user"
                }
            
        except Exception as e:
            logger.error(f"Failed to clear all URLs: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_response(self, user_id: int, query: str, chat_history: Optional[List[tuple]] = None) -> str:
        """Get a response to a query using the user's indexed URLs - consistent with document RAG"""
        try:
            collection_name = self._collection_name(user_id)
            
            try:
                collection = self.chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            except Exception:
                raise Exception("No indexed URLs found. Please add URLs first.")
            
            # Query collection
            results = collection.query(
                query_texts=[query],
                n_results=5
            )
            
            if not results["documents"][0]:
                raise Exception("No relevant information found in the indexed URLs.")
            
            # Prepare context
            context_chunks = results["documents"][0]
            context = "\n".join(context_chunks)
            
            # Build conversation history context
            history_context = ""
            if chat_history:
                history_parts = []
                for user_msg, assistant_msg in chat_history[-5:]:  # Last 5 exchanges
                    history_parts.append(f"User: {user_msg}")
                    history_parts.append(f"Assistant: {assistant_msg}")
                history_context = "\n".join(history_parts) + "\n\n"
            
            # Generate response with consistent format
            prompt = f"""{history_context}Context information from indexed web pages:
{context}

Current question: {query}

Provide a helpful and accurate answer based on the context from the web pages. If the information isn't available in the context, say you don't know. Be conversational and natural in your response."""
            
            response = self.llm.invoke(prompt)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Failed to get response: {str(e)}")
            raise Exception(str(e))
    
    def get_sources_for_query(self, user_id: int, query: str) -> List[Dict[str, str]]:
        """Get sources used for a query - for reference/citation purposes"""
        try:
            collection_name = self._collection_name(user_id)
            
            try:
                collection = self.chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            except Exception:
                return []
            
            # Query collection
            results = collection.query(
                query_texts=[query],
                n_results=5
            )
            
            if not results["documents"][0]:
                return []
            
            # Extract unique sources
            sources = []
            seen_urls = set()
            
            for metadata in results["metadatas"][0]:
                url = metadata.get("url")
                title = metadata.get("title")
                
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    sources.append({
                        "url": url,
                        "title": title
                    })
            
            return sources
            
        except Exception as e:
            logger.error(f"Failed to get sources: {str(e)}")
            return []