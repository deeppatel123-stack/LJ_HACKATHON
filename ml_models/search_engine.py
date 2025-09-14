from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class SemanticSearchEngine:
    """
    Manages semantic search using SentenceTransformers for embeddings
    and FAISS for vector indexing.
    """
    
    def __init__(self):
        # Load a pre-trained SentenceTransformer model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []  # Stores (doc_id, text) tuples
        self.document_ids = []
        self.embeddings = None
        self.index = None
        
    def add_document(self, doc_id: int, text: str):
        """Adds a document to the index."""
        self.documents.append((doc_id, text))
        self.document_ids.append(doc_id)
        
        # We'll re-index the entire corpus for simplicity
        self.rebuild_index()
        
    def rebuild_index(self):
        """Generates embeddings and rebuilds the FAISS index."""
        if not self.documents:
            return
            
        doc_texts = [doc[1] for doc in self.documents]
        self.embeddings = self.model.encode(doc_texts, convert_to_tensor=False)
        
        # Build FAISS index
        embedding_dim = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(embedding_dim)  # L2 distance
        self.index.add(np.array(self.embeddings).astype('float32'))
    
    def search(self, query: str, top_k: int = 5):
        """Performs a semantic search."""
        if self.index is None:
            return []
            
        query_embedding = self.model.encode(query, convert_to_tensor=False).reshape(1, -1).astype('float32')
        
        # Search the index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get the document IDs and their relevance scores
        results = []
        for i, doc_index in enumerate(indices[0]):
            if doc_index >= 0 and doc_index < len(self.document_ids):
                results.append({
                    'document_id': self.document_ids[doc_index],
                    'score': float(distances[0][i])
                })
        
        return results