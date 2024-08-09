from langchain_community.graphs import Neo4jGraph
from langchain_text_splitters import TokenTextSplitter
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.retrievers.document_compressors import (
    EmbeddingsFilter,
    DocumentCompressorPipeline,
)
from langchain.retrievers import ContextualCompressionRetriever
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch
from langchain_core.chat_history import BaseChatMessageHistory

from src.client.llm import LLMModel
from src.config import (
    CHAT_DOC_SPLIT_SIZE,
    CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD,
    CHAT_SEARCH_KWARG_K,
    CHAT_SEARCH_KWARG_SCORE_THRESHOLD,
)
from src.templates import QUESTION_TRANSFORM_TEMPLATE, VECTOR_GRAPH_SEARCH_QUERY


class DataRetriever:
    def __init__(
        self,
        graphdb_client: Neo4jGraph,
        llm_model: LLMModel = LLMModel,
        search_k: int = CHAT_SEARCH_KWARG_K,
        score_threshold: float = CHAT_SEARCH_KWARG_SCORE_THRESHOLD,
    ):
        self.llm_model = llm_model
        self.graphdb_client = graphdb_client
        self.search_k = search_k
        self.score_threshold = score_threshold
        self.vector_db = Neo4jVector.from_existing_index(
            embedding=self.llm_model.get_embedding_model(),
            index_name="vector",
            retrieval_query=VECTOR_GRAPH_SEARCH_QUERY,
            graph=self.graphdb_client,
        )

        self.vector_retriever = self._get_vector_retriever()
        self.document_retriever_chain = DocumentRetrieverChain(
            llm=self.llm_model, retriever=self.vector_retriever
        ).create_chain()

    def _get_vector_retriever(self):
        search_kwargs = {"k": self.search_k, "score_threshold": self.score_threshold}
        return self.vector_db.as_retriever(search_kwargs=search_kwargs)

    def get_data(self, history: BaseChatMessageHistory):
        return self.document_retriever_chain.invoke({"messages": history.messages})


class DocumentRetrieverChain:
    def __init__(self, llm: LLMModel, retriever: VectorStoreRetriever):
        self.llm = llm
        self.retriever = retriever

    def create_query_transform_prompt(self):
        return ChatPromptTemplate.from_messages(
            [
                ("system", QUESTION_TRANSFORM_TEMPLATE),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    def create_pipeline_compressor(self):
        splitter = TokenTextSplitter(chunk_size=CHAT_DOC_SPLIT_SIZE, chunk_overlap=0)
        embedding_model = self.llm.get_embedding_model()
        embeddings_filter = EmbeddingsFilter(
            embeddings=embedding_model,
            similarity_threshold=CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD,
        )
        return DocumentCompressorPipeline(transformers=[splitter, embeddings_filter])

    def create_compression_retriever(self, pipeline_compressor):
        return ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=self.retriever
        )

    def create_query_transforming_retriever_chain(
        self, query_transform_prompt, compression_retriever
    ):
        output_parser = StrOutputParser()
        return RunnableBranch(
            (
                lambda x: len(x.get("messages", [])) == 1,
                (lambda x: x["messages"][-1].content) | compression_retriever,
            ),
            query_transform_prompt
            | self.llm.get_chat_anthropic()
            | output_parser
            | compression_retriever,
        ).with_config(run_name="chat_retriever_chain")

    def create_chain(self):
        query_transform_prompt = self.create_query_transform_prompt()
        pipeline_compressor = self.create_pipeline_compressor()
        compression_retriever = self.create_compression_retriever(pipeline_compressor)
        query_transforming_retriever_chain = (
            self.create_query_transforming_retriever_chain(
                query_transform_prompt, compression_retriever
            )
        )
        return query_transforming_retriever_chain
