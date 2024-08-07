import json
from typing import List, Dict, Any, Tuple
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import TokenTextSplitter
from langchain.retrievers.document_compressors import (
    EmbeddingsFilter,
    DocumentCompressorPipeline,
)
from langchain.retrievers import ContextualCompressionRetriever
from langchain_core.runnables import RunnableBranch
from langchain_community.graphs import Neo4jGraph

from .config import (
    CHAT_DOC_SPLIT_SIZE,
    CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD,
    CHAT_SEARCH_KWARG_K,
    CHAT_SEARCH_KWARG_SCORE_THRESHOLD,
)
from .templates import (
    CHAT_SYSTEM_TEMPLATE,
    QUESTION_TRANSFORM_TEMPLATE,
    VECTOR_GRAPH_SEARCH_ENTITY_LIMIT,
    VECTOR_GRAPH_SEARCH_QUERY,
)
from src.llm import get_llm_model, get_embedding_model
from langchain_google_vertexai.model_garden import ChatAnthropicVertex


def summarize_messages(
    llm: ChatAnthropicVertex,
    history: Neo4jChatMessageHistory,
    stored_messages: List[Dict[str, Any]],
) -> bool:
    if not stored_messages:
        return False

    summarization_prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",
                "Summarize the above chat messages into a concise message, focusing on key points and relevant details that could be useful for future conversations. Exclude all introductions and extraneous information.",
            ),
        ]
    )

    summarization_chain = summarization_prompt | llm
    summary_message = summarization_chain.invoke({"chat_history": stored_messages})

    history.clear()
    history.add_user_message("Our current conversation summary till now")
    history.add_message(summary_message)
    return True


def get_neo4j_retriever(
    graph: Neo4jGraph,
    retrieval_query: str,
    index_name: str = "vector",
    search_k: int = CHAT_SEARCH_KWARG_K,
    score_threshold: float = CHAT_SEARCH_KWARG_SCORE_THRESHOLD,
) -> VectorStoreRetriever:
    embedding_model, _ = get_embedding_model()
    neo_db = Neo4jVector.from_existing_index(
        embedding=embedding_model,
        index_name=index_name,
        retrieval_query=retrieval_query,
        graph=graph,
    )

    search_kwargs = {"k": search_k, "score_threshold": score_threshold}
    return neo_db.as_retriever(search_kwargs=search_kwargs)


def create_document_retriever_chain(
    llm: ChatAnthropicVertex, retriever: VectorStoreRetriever
):
    def create_query_transform_prompt():
        return ChatPromptTemplate.from_messages(
            [
                ("system", QUESTION_TRANSFORM_TEMPLATE),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

    def create_pipeline_compressor():
        splitter = TokenTextSplitter(chunk_size=CHAT_DOC_SPLIT_SIZE, chunk_overlap=0)
        embedding_model, _ = get_embedding_model()
        embeddings_filter = EmbeddingsFilter(
            embeddings=embedding_model,
            similarity_threshold=CHAT_EMBEDDING_FILTER_SCORE_THRESHOLD,
        )
        return DocumentCompressorPipeline(transformers=[splitter, embeddings_filter])

    def create_compression_retriever(pipeline_compressor):
        return ContextualCompressionRetriever(
            base_compressor=pipeline_compressor, base_retriever=retriever
        )

    def create_query_transforming_retriever_chain(
        query_transform_prompt, compression_retriever
    ):
        output_parser = StrOutputParser()
        return RunnableBranch(
            (
                lambda x: len(x.get("messages", [])) == 1,
                (lambda x: x["messages"][-1].content) | compression_retriever,
            ),
            query_transform_prompt | llm | output_parser | compression_retriever,
        ).with_config(run_name="chat_retriever_chain")

    query_transform_prompt = create_query_transform_prompt()
    pipeline_compressor = create_pipeline_compressor()
    compression_retriever = create_compression_retriever(pipeline_compressor)
    query_transforming_retriever_chain = create_query_transforming_retriever_chain(
        query_transform_prompt, compression_retriever
    )

    return query_transforming_retriever_chain


def setup_chat(graph: Neo4jGraph, retrieval_query: str):
    llm = get_llm_model()
    retriever = get_neo4j_retriever(graph=graph, retrieval_query=retrieval_query)
    doc_retriever = create_document_retriever_chain(llm, retriever)
    return llm, doc_retriever


def format_documents(documents: List[Dict[str, Any]]) -> Tuple[str, set]:
    prompt_token_cutoff = 4
    sorted_documents = sorted(
        documents, key=lambda doc: doc.state["query_similarity_score"], reverse=True
    )[:prompt_token_cutoff]

    formatted_docs = []
    sources = set()

    for doc in sorted_documents:
        source = doc.metadata["source"]
        sources.add(source)
        formatted_doc = (
            f"Document start\n"
            f"This Document belongs to the source {source}\n"
            f"Content: {doc.page_content}\n"
            f"Document end\n"
        )
        formatted_docs.append(formatted_doc)

    return "\n\n".join(formatted_docs), sources


def get_rag_chain(llm, system_template: str = CHAT_SYSTEM_TEMPLATE):
    question_answering_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "User question: {input}"),
        ]
    )
    return question_answering_prompt | llm


def get_sources_and_chunks(
    sources_used: List[str], docs: List[Dict[str, Any]]
) -> Dict[str, Any]:
    chunkdetails_list = []
    sources_used_set = set(sources_used)

    for doc in docs:
        source = doc.metadata["source"]
        if source in sources_used_set:
            chunkdetails = [
                {**chunkdetail, "score": round(chunkdetail["score"], 4)}
                for chunkdetail in doc.metadata["chunkdetails"]
            ]
            chunkdetails_list.extend(chunkdetails)

    return {"sources": sources_used, "chunkdetails": chunkdetails_list}


def process_documents(
    docs: List[Dict[str, Any]],
    question: str,
    messages: List[Dict[str, Any]],
    llm,
) -> Tuple[str, Dict[str, Any]]:
    formatted_docs, sources = format_documents(docs)
    rag_chain = get_rag_chain(llm=llm)
    ai_response = rag_chain.invoke(
        {"messages": messages[:-1], "context": formatted_docs, "input": question}
    )
    result = get_sources_and_chunks(sources, docs)
    return ai_response.content, result


def QA_RAG_Vector_Graph(
    graph: Neo4jGraph, question: str, session_id: str
) -> Dict[str, Any]:
    try:
        history = Neo4jChatMessageHistory(graph=graph, session_id=session_id)
        messages = history.messages

        user_question = HumanMessage(content=question)
        messages.append(user_question)

        retrieval_query = VECTOR_GRAPH_SEARCH_QUERY.format(
            no_of_entites=VECTOR_GRAPH_SEARCH_ENTITY_LIMIT
        )

        llm, doc_retriever = setup_chat(graph, retrieval_query)

        docs = doc_retriever.invoke({"messages": messages})

        if docs:
            content, result = process_documents(docs, question, messages, llm)
        else:
            content = "I couldn't find any relevant documents to answer your question."
            result = {"sources": [], "chunkdetails": []}

        ai_response = AIMessage(content=content)
        messages.append(ai_response)
        summarize_messages(llm, history, messages)

        return {
            "session_id": session_id,
            "message": content,
            "info": {
                "sources": result["sources"],
                "chunkdetails": result["chunkdetails"],
                "total_tokens": 0,  # You might want to implement token counting
                "response_time": 0,  # You might want to implement response time tracking
                "mode": "vector and graph",
            },
            "user": "chatbot",
        }

    except Exception as e:
        error_name = type(e).__name__
        return {
            "session_id": session_id,
            "message": "Something went wrong",
            "info": {
                "sources": [],
                "chunkids": [],
                "error": f"{error_name}: {str(e)}",
                "mode": "vector and graph",
            },
            "user": "chatbot",
        }
