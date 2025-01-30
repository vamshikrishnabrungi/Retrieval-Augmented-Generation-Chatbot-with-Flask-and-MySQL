import json
from typing import List, Dict
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

class VectorStore:
    """A class for storing and retrieving text chunks using FAISS and sentence embeddings."""
    
    def __init__(self):
        """Initialize the vector store with a sentence transformer model and FAISS index."""
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Embedding model
        self.index = None  # FAISS index
        self.chunks = []   # List of text chunks

    def load_data(self, data_file: str = "processed_data.json"):
        """Load processed chunks from JSON file."""
        try:
            with open(data_file, 'r') as f:
                self.chunks = json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def create_index(self):
        """Create FAISS index from text chunks with error handling."""
        if not self.chunks:
            raise ValueError("No chunks available to create index.")

        try:
            # Get embeddings for all chunks
            texts = [chunk['text'] for chunk in self.chunks]
            embeddings = self.model.encode(texts)

            # Initialize FAISS index
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)

            # Add vectors to the index
            self.index.add(np.array(embeddings).astype('float32'))
        except Exception as e:
            print(f"Error creating index: {e}")
            raise

    def search(self, query: str, k: int = 3) -> List[Dict[str, str]]:
        """Search for most relevant chunks given a query."""
        if not self.index:
            raise ValueError("Index not initialized. Call create_index() first.")

        try:
            # Get query embedding
            query_vector = self.model.encode([query])[0].reshape(1, -1)

            # Search in FAISS index
            distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)

            # Return relevant chunks
            results = []
            for idx in indices[0]:
                results.append(self.chunks[idx])

            return results
        except Exception as e:
            print(f"Error searching index: {e}")
            raise

    def save_index(self, filename: str = "faiss_index.bin"):
        """Save FAISS index to disk."""
        if self.index is not None:
            faiss.write_index(self.index, filename)
            
    def load_index(self, filename: str = "faiss_index.bin"):
        """Load FAISS index from disk."""
        self.index = faiss.read_index(filename)

if __name__ == "__main__":
    # Initialize and test vector store
    vector_store = VectorStore()
    vector_store.load_data()
    vector_store.create_index()
    vector_store.save_index()
    
    # Test search
    test_query = "What is the Apollo mission?"
    results = vector_store.search(test_query)
    print(f"Test query: {test_query}")
    for result in results:
        print(f"Result: {result['text'][:200]}...")