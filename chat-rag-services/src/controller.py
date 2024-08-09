from typing import Dict, Any
from langchain_community.chat_message_histories import Neo4jChatMessageHistory
from src.processor.completions import QAEngine
from src.processor.qa_tools import summarize_history


def get_chat_completions(
    qa_engine: QAEngine, question: str, session_id: str
) -> Dict[str, Any]:
    try:
        history = Neo4jChatMessageHistory(graph=qa_engine.db, session_id=session_id)
        resp, metadata = qa_engine.get_answer(question, history)
        summarize_history(history)

        return {
            "session_id": session_id,
            "message": resp,
            "info": metadata,
        }
    except Exception as e:
        error_name = type(e).__name__
        raise Exception(f"Error: {error_name} - {str(e)}")
