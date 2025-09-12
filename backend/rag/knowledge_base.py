import os
import shutil
from typing import List
from langchain_community.vectorstores import FAISS
#--- from langchain_openai import OpenAIEmbeddings #- COMMENTED OUT
from langchain_google_genai import GoogleGenerativeAIEmbeddings #- NEW: Import for Gemini
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from settings import settings

class VectorStore:
    """
    Manages a FAISS vector store using Google Gemini embeddings.
    This implementation is session-specific, creating a new index for each API call.
    """
    def __init__(self, index_path: str):
        #- UPDATED: Check for the Gemini API key instead of OpenAI's
        if not settings.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is not configured. Please set it in your .env file.")
        
        self.index_path = index_path
        
        #- COMMENTED OUT the OpenAI embeddings model
        # self.embeddings_model = OpenAIEmbeddings(
        #     api_key=settings.OPENAI_API_KEY,
        #     model=settings.EMBEDDING_MODEL_NAME
        # )

        #- NEW: Initialize the Gemini embeddings model
        self.embeddings_model = GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GEMINI_API_KEY,
            model="models/embedding-001" # The standard model for Gemini embeddings
        )

        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=250)
        self.db = None

    def create_and_store(self, documents: List[Document]):
        """
        Splits documents into chunks, generates embeddings, builds a FAISS index,
        and saves it locally.
        """
        chunks = self.text_splitter.split_documents(documents)
        print(f"💎 Creating FAISS index from {len(chunks)} text chunks using Gemini.")

        if not chunks:
            print("No text chunks to store. Skipping index creation.")
            return

        self.db = FAISS.from_documents(chunks, self.embeddings_model)
        self.db.save_local(self.index_path)
        print(f"FAISS index successfully created and saved at: {self.index_path}")

    def retrieve(self, query: str, n_results: int = 7) -> str:
        """
        Loads the FAISS index and performs a similarity search to retrieve relevant context.
        """
        if not os.path.exists(self.index_path):
            return "Error: FAISS index not found. Please ensure the knowledge base was created."

        if self.db is None:
            self.db = FAISS.load_local(
                self.index_path,
                self.embeddings_model,
                allow_dangerous_deserialization=True 
            )

        results = self.db.similarity_search(query, k=n_results)
        return "\n---\n".join([doc.page_content for doc in results])

    def cleanup(self):
        """Removes the directory containing the FAISS index to save space."""
        if os.path.exists(self.index_path):
            shutil.rmtree(self.index_path)
            print(f"Cleaned up FAISS index at: {self.index_path}")