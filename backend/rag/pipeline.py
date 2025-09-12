import os
import uuid
from typing import List
from .loaders import load_document
from .knowledge_base import VectorStore
from settings import settings

class RAGPipeline:
    """
    Integrates the full FAISS-based RAG workflow.
    Manages the lifecycle of a temporary FAISS index for a single request.
    """
    def __init__(self, file_paths: List[str]):
        # Create a unique directory for this session's FAISS index
        session_id = uuid.uuid4().hex
        self.index_path = os.path.join(settings.FAISS_INDEX_PATH, f"session_{session_id}")
        
        self.vector_store = VectorStore(index_path=self.index_path)
        self._initialize_knowledge_base(file_paths)

    def _initialize_knowledge_base(self, file_paths: List[str]):
        """Loads all documents and builds the FAISS vector store."""
        print("Initializing FAISS knowledge base...")
        all_docs = []
        for file_path in file_paths:
            docs = load_document(file_path)
            all_docs.extend(docs)
        
        if all_docs:
            self.vector_store.create_and_store(all_docs)
        else:
            print("Warning: No documents were loaded to create the knowledge base.")

    def retrieve_context(self, query: str) -> str:
        """Retrieves relevant context for a given query from the FAISS index."""
        return self.vector_store.retrieve(query)

    def cleanup(self):
        """Cleans up the resources used by the pipeline (i.e., the FAISS index)."""
        self.vector_store.cleanup()