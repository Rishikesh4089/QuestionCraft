# from typing import List
# from openai import OpenAI
# from ..settings import settings

# class EmbeddingModel:
#     """
#     A wrapper class for OpenAI's embedding models.
#     """
#     def __init__(self):
#         if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key_here":
#             raise ValueError("OPENAI_API_KEY is not configured. Please set it in your .env file.")
#         self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
#         self.model_name = settings.EMBEDDING_MODEL_NAME

#     def generate_embeddings(self, text_chunks: List[str]) -> List[List[float]]:
#         """
#         Generates embeddings for a list of text chunks using the configured OpenAI model.
#         """
#         response = self.client.embeddings.create(
#             input=text_chunks,
#             model=self.model_name
#         )
#         return [embedding.embedding for embedding in response.data]