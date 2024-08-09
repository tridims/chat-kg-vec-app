from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai.model_garden import ChatAnthropicVertex
from langchain_openai import AzureChatOpenAI

from src.config import ANTHROPIC_MODEL_NAME, ANTHROPIC_REGION


class LLMModel:
    _embedding_instance = None
    _llm_instance_anthropic = None
    _llm_instance_openai = None

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
    def get_chat_anthropic(cls) -> ChatAnthropicVertex:
        if cls._llm_instance_anthropic is None:
            llm = ChatAnthropicVertex(
                location=ANTHROPIC_REGION,
                model_name=ANTHROPIC_MODEL_NAME,
            )
            cls._llm_instance_anthropic = llm
        return cls._llm_instance_anthropic

    @classmethod
    def get_chat_openai(cls) -> AzureChatOpenAI:
        if cls._llm_instance_openai is None:
            llm = AzureChatOpenAI(azure_deployment="gpt-35-turbo")
            cls._llm_instance_openai = llm
        return cls._llm_instance_openai
