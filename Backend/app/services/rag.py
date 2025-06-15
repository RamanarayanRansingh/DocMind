from typing import Optional, List, Dict
import PyPDF2
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from ..config import Settings
import chromadb
import shutil
import os
import uuid
import logging
import hashlib
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

class RAGService:
    def __init__(self, persist_directory: str = "chroma_db"):
        self.persist_directory = persist_directory
        os.makedirs(self.persist_directory, exist_ok=True)
        self.collection_name_template = "doc_{document_id}"
        
        # Initialize components
        self.embedding_function = SentenceTransformerEmbedding()
        self.llm = ChatGroq(
            temperature=0.3,
            model_name="llama3-70b-8192",  # Updated model name
            groq_api_key=Settings().GROQ_API_KEY,
            max_tokens=1024
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", ".", " ", ""]
        )
        
        # Initialize ChromaDB client
        try:
            self.chroma_client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=chromadb.Settings(anonymized_telemetry=False)
            )
            logger.info("ChromaDB client initialized successfully")
        except Exception as e:
            logger.error(f"ChromaDB initialization failed: {str(e)}")
            raise

    def _collection_name(self, document_id: int) -> str:
        return self.collection_name_template.format(document_id=document_id)
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of file contents"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def _load_existing_collections(self):
            """Load existing collections from ChromaDB"""
            try:
        # Get list of collection names (strings)
                collection_names = self.chroma_client.list_collections()
        
                for collection_name in collection_names:
                    if collection_name.startswith("doc_"):
                        doc_id = int(collection_name.split("_")[1])
                        self.document_collections[doc_id] = collection_name
                
                        try:
                    # Get collection properly with embedding function
                            collection = self.chroma_client.get_collection(
                                name=collection_name,
                                embedding_function=self.embedding_function
                            )
                    
                    # Get metadata from first item
                            items = collection.peek(1)
                            if items['metadatas']:
                                self.document_hashes[doc_id] = items['metadatas'][0].get('file_hash', '')
                        
                        except Exception as e:
                            logger.warning(f"Couldn't load metadata for {collection_name}: {str(e)}")
        
                logger.info(f"Loaded {len(self.document_collections)} existing collections")
        
            except Exception as e:
                logger.error(f"Failed to load collections: {str(e)}")
                raise
    
    def process_document(self, document_id: int, file_path: str, file_type: str) -> None:
        try:
            current_hash = self._calculate_file_hash(file_path)
            collection_name = self._collection_name(document_id)

            # Check existing collection directly in ChromaDB
            try:
                collection = self.chroma_client.get_collection(collection_name)
                existing_hash = collection.peek(1)['metadatas'][0].get('file_hash', '')
                if existing_hash == current_hash:
                    logger.info(f"Document {document_id} unchanged")
                    return
                self.chroma_client.delete_collection(collection_name)
            except Exception as e:
                logger.info(f"Creating new collection for document {document_id}")

            # Process document
            text = self._extract_text(file_path, file_type)
            chunks = self.text_splitter.split_text(text)
            
            # Create new collection
            collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )

            # Add documents with metadata
            batch_size = 100
            for i in range(0, len(chunks), batch_size):
                batch_chunks = chunks[i:i + batch_size]
                batch_ids = [str(uuid.uuid4()) for _ in batch_chunks]
                batch_metadata = [{'file_hash': current_hash} for _ in batch_chunks]
                
                collection.add(
                    documents=batch_chunks,
                    ids=batch_ids,
                    metadatas=batch_metadata
                )

            logger.info(f"Processed document {document_id} with {len(chunks)} chunks")

        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            self.cleanup_document(document_id)
            raise

    
    def get_response(self, document_id: int, query: str) -> str:
        try:
            collection_name = self._collection_name(document_id)
            
            try:
                collection = self.chroma_client.get_collection(
                    name=collection_name,
                    embedding_function=self.embedding_function
                )
            except Exception as e:
                logger.error(f"Collection {collection_name} not found: {str(e)}")
                return "Document not found in the database"

            results = collection.query(
                query_texts=[query],
                n_results=3
            )
            
            if not results['documents'][0]:
                return "No relevant information found in the document."
            
            context = "\n".join(results['documents'][0])
            prompt = f"""Context information:
{context}

Question: {query}

Provide a concise answer based on the context. If unsure, say you don't know."""
            
            response = self.llm.invoke(prompt)
            return response.content.strip()

        except Exception as e:
            logger.error(f"Response generation failed: {str(e)}")
            return "An error occurred while processing your request."
    
    def cleanup_document(self, document_id: int) -> None:
        try:
            collection_name = self._collection_name(document_id)
            self.chroma_client.delete_collection(collection_name)
            logger.info(f"Cleaned up document {document_id}")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

    def _extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from supported file types"""
        try:
            if file_type == 'pdf':
                return self._extract_from_pdf(file_path)
            elif file_type in ['csv', 'xlsx', 'xls']:
                return self._extract_from_spreadsheet(file_path, file_type)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise


    def _extract_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text() or ""
                    text.append(page_text)
            return "\n".join(text)
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise

    def _extract_from_spreadsheet(self, file_path: str, file_type: str) -> str:
        """Extract text from spreadsheet files"""
        try:
            if file_type == 'csv':
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            return df.to_string(index=False)
        except Exception as e:
            logger.error(f"Spreadsheet extraction failed: {str(e)}")
            raise