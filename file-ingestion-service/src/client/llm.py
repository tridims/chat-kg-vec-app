from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai.model_garden import ChatAnthropicVertex


class LLMModel:
    _embedding_instance = None
    _llm_instance = None

    @classmethod
    def get_embedding_model(cls) -> VertexAIEmbeddings:
        if cls._embedding_instance is None:
            cls._embedding_instance = VertexAIEmbeddings(
                model="textembedding-gecko@003"
            )
            # dimension = 768
            # cls._embedding_instance = (embeddings, dimension)
        return cls._embedding_instance

    @classmethod
    def get_chat_model(cls) -> ChatAnthropicVertex:
        if cls._llm_instance is None:
            llm = ChatAnthropicVertex(
                model_name="claude-3-5-sonnet@20240620",
                project="global-river-423404-p3",
                location="us-east5",
            )
            cls._llm_instance = llm
        return cls._llm_instance
