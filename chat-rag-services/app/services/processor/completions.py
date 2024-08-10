from typing import Any, Dict, List, Set, Tuple
from langchain_community.graphs import Neo4jGraph
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.db.llm import LLMModel
from app.services.processor.context_retriever import DataRetriever
from app.models.templates import CHAT_SYSTEM_TEMPLATE


class QAEngine:
    def __init__(self, db: Neo4jGraph, llm: LLMModel = LLMModel):
        self.db = db
        self.llm = llm
        self.data_retriever = DataRetriever(graphdb_client=self.db)

    def get_answer(self, question: str, history: BaseChatMessageHistory):
        history.add_message(HumanMessage(content=question))

        context_document = self.data_retriever.get_data(history)
        added_context, sources = self._format_context_docs(context_document)

        rag_chain = self._get_rag_chain()
        result = rag_chain.invoke(
            {
                # "messages": history.messages[:-1],
                "messages": history.messages,
                "context": added_context,
                "input": question,
            }
        )
        chunk_list = self._parse_source_docs(docs=context_document)
        history.add_ai_message(AIMessage(content=result.content))

        return result.content, {"sources": sources, "chunk_details": chunk_list}

    def _format_context_docs(self, docs: List[Dict[str, Any]]) -> Tuple[str, set]:
        take = 5
        sorted_docs = sorted(
            docs, key=lambda doc: doc.state["query_similarity_score"], reverse=True
        )[:take]

        formatted_docs = []
        sources = set()
        for doc in sorted_docs:
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

    def _get_rag_chain(self, system_template: str = CHAT_SYSTEM_TEMPLATE):
        question_answering_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_template),
                MessagesPlaceholder(variable_name="messages"),
                ("human", "User question: {input}"),
            ]
        )

        return question_answering_prompt | self.llm.get_chat_openai()

    def _parse_source_docs(self, docs: List[Dict[str, Any]]) -> Tuple[List, Set]:
        chunk_list = []

        for doc in docs:
            chunkdetails = [
                {**chunkdetail, "score": round(chunkdetail["score"], 4)}
                for chunkdetail in doc.metadata["chunkdetails"]
            ]
            chunk_list.extend(chunkdetails)

        return chunk_list
