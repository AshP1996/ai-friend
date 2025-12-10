"""
Advanced semantic memory with embeddings and vector search
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import uuid
from utils.logger import Logger

class SemanticMemoryEngine:
    def __init__(self):
        self.logger = Logger("SemanticMemory")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = chromadb.Client()
        self.collections = {}  # Per-user collections
    
    def get_collection(self, user_id: str):
        if user_id not in self.collections:
            collection_name = f"memories_{user_id}"
            self.collections[user_id] = self.chroma_client.create_collection(
                name=collection_name,
                get_or_create=True
            )
        return self.collections[user_id]
    
    async def save_memory(self, user_id: str, content: str, metadata: Dict[str, Any]):
        '''Save memory with semantic embedding'''
        collection = self.get_collection(user_id)
        
        # Generate embedding
        embedding = self.model.encode(content).tolist()
        
        memory_id = str(uuid.uuid4())
        collection.add(
            embeddings=[embedding],
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        self.logger.info(f"Saved memory for user {user_id}: {content[:50]}...")
        return memory_id
    
    async def search_memories(self, user_id: str, query: str, n_results: int = 5) -> List[Dict]:
        '''Semantic search through memories'''
        collection = self.get_collection(user_id)
        
        query_embedding = self.model.encode(query).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        memories = []
        if results['documents']:
            for i, doc in enumerate(results['documents'][0]):
                memories.append({
                    'content': doc,
                    'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                    'distance': results['distances'][0][i] if results['distances'] else 0
                })
        
        return memories
    
    async def delete_memory(self, user_id: str, memory_id: str):
        '''Delete specific memory'''
        collection = self.get_collection(user_id)
        collection.delete(ids=[memory_id])
        self.logger.info(f"Deleted memory {memory_id} for user {user_id}")

