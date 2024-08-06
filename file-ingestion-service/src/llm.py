from langchain_google_vertexai import VertexAIEmbeddings
from langchain_google_vertexai.model_garden import ChatAnthropicVertex


def get_embedding_model():
    embeddings = VertexAIEmbeddings(model="textembedding-gecko@003")
    dimension = 768

    return embeddings, dimension


def get_llm_model():
    llm = ChatAnthropicVertex(
        model_name="claude-3-5-sonnet@20240620",
        project="global-river-423404-p3",
        location="us-east5",
    )

    return llm
