"""Embeddings and vector database integration with Pinecone."""
from typing import List
from pinecone import Pinecone, ServerlessSpec
from app.chatbot.config import (
    PINECONE_API_KEY, PINECONE_INDEX_NAME, PINECONE_ENVIRONMENT
)


class PineconeVectorDB:
    """Manage Pinecone vector database operations with serverless embeddings."""

    def __init__(self):
        if not PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY not configured")
        
        self.pc = Pinecone(api_key=PINECONE_API_KEY)
        self.index_name = PINECONE_INDEX_NAME
        self._ensure_index_exists()

    def _ensure_index_exists(self):
        """Create index with serverless embeddings if it doesn't exist."""
        indexes = [idx.name for idx in self.pc.list_indexes()]
        if self.index_name not in indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=1536,  # OpenAI/Pinecone inference dimension
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region=PINECONE_ENVIRONMENT
                )
            )

    def store_chunks(self, chunks: List[str], document_id: str, user_id: int) -> int:
        """Store document chunks in Pinecone using serverless embeddings."""
        index = self.pc.Index(self.index_name)
        vectors_to_upsert = []
        
        for i, chunk in enumerate(chunks):
            vector_id = f"{document_id}_{i}"
            metadata = {
                "document_id": str(document_id),
                "user_id": str(user_id),
                "chunk_index": i,
                "text": chunk[:500]
            }
            vectors_to_upsert.append({
                "id": vector_id,
                "values": [],  # Let Pinecone inference generate embeddings
                "metadata": metadata,
                "sparse_values": None,
                "data": chunk
            })
        
        # Use upsert with data field for serverless embeddings
        index.upsert(vectors=vectors_to_upsert)
        return len(vectors_to_upsert)

    def search_chunks(self, query: str, document_id: str, top_k: int = 5) -> List[dict]:
        """Search for relevant chunks using Pinecone inference."""
        index = self.pc.Index(self.index_name)
        
        # Query with text directly - Pinecone will handle embedding
        results = index.query(
            data=query,
            top_k=top_k,
            filter={"document_id": {"$eq": str(document_id)}},
            include_metadata=True
        )
        
        return [
            {
                "text": match.metadata.get("text", ""),
                "chunk_index": match.metadata.get("chunk_index", 0),
                "score": match.score
            }
            for match in results.matches
        ]

    def delete_document_vectors(self, document_id: str):
        """Delete all vectors for a document."""
        index = self.pc.Index(self.index_name)
        index.delete(
            filter={"document_id": {"$eq": str(document_id)}}
        )
