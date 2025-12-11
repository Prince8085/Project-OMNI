"""
RAG Module for OMNI.
Handles document ingestion and retrieval using ChromaDB.
"""

import os
import logging
from typing import List, Optional
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

logger = logging.getLogger(__name__)

class RAGModule:
    def __init__(self, persist_dir: str = "data/memory"):
        self.persist_dir = persist_dir
        
        # Initialize Embeddings (Local, fast)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize Vector DB
        if not os.path.exists(persist_dir):
            os.makedirs(persist_dir, exist_ok=True)
            
        self.db = Chroma(
            persist_directory=persist_dir,
            embedding_function=self.embeddings,
            collection_name="omni_knowledge"
        )
        
        logger.info(f"RAG Module initialized at {persist_dir}")

    def ingest_file(self, file_path: str) -> str:
        """Ingest a file (PDF/TXT) into the knowledge base."""
        try:
            if not os.path.exists(file_path):
                return f"Error: File not found: {file_path}"
                
            # Load
            if file_path.lower().endswith('.pdf'):
                loader = PyPDFLoader(file_path)
            else:
                loader = TextLoader(file_path, encoding='utf-8')
            
            docs = loader.load()
            
            # Split
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            # Add to DB
            self.db.add_documents(splits)
            self.db.persist()
            
            return f"Successfully ingested {len(splits)} chunks from {os.path.basename(file_path)}"
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            return f"Ingestion failed: {e}"

    def query(self, query_text: str, k: int = 3) -> str:
        """Search the knowledge base."""
        try:
            results = self.db.similarity_search(query_text, k=k)
            if not results:
                return ""
            
            context = "\n\n".join([doc.page_content for doc in results])
            return context
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return ""
