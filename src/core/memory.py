"""
Long-Term Memory Module using ChromaDB.
Stores and retrieves conversation history and user preferences.
"""
import chromadb
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OmniMemory:
    """Vector database memory for OMNI."""
    
    def __init__(self, persist_path="memory_db"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(
            name="omni_memory",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"✓ Memory initialized with {self.collection.count()} items")
        
    def add(self, text: str, metadata: dict = None):
        """Add a memory."""
        if not metadata:
            metadata = {}
        
        metadata['timestamp'] = datetime.now().isoformat()
        
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[str(uuid.uuid4())]
        )
        logger.info(f"Memory added: {text[:30]}...")
        
    def search(self, query: str, n_results: int = 3):
        """Search for relevant memories."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        if not results['documents']:
            return []
            
        return results['documents'][0]

    def get_context(self, query: str) -> str:
        """Get formatted context string for LLM."""
        memories = self.search(query)
        if not memories:
            return ""
            
        context = "Relevant Past Info:\n"
        for m in memories:
            context += f"- {m}\n"
        return context

if __name__ == "__main__":
    m = OmniMemory()
    m.add("User likes the color blue.")
    print(m.search("What color do I like?"))
