import chunk
from src.config import MAX_EMBEDDING_WORKER, MAX_PARALLEL_EMBEDDING_SIZE
from src.models.chunk import ChunkEmbedding, ChunkDocument
from src.utils import batch
from src.client.llm import LLMModel
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List


class EmbeddingGenerator:
    def __init__(self, model: LLMModel):
        self.model = model

    def generate_embeddings(
        self, documents: List[ChunkDocument]
    ) -> List[ChunkEmbedding]:
        embeddings = self.model.get_embedding_model().embed(
            texts=[doc.chunk_doc.page_content for doc in documents],
            embeddings_task_type="RETRIEVAL_QUERY",
        )

        chunk_embeddings = []
        for doc, emb in zip(documents, embeddings):
            chunk_embeddings.append(
                ChunkEmbedding(chunk_id=doc.chunk_id, embedding=emb)
            )

        return chunk_embeddings
