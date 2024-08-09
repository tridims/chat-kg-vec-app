from src.client.llm import LLMModel
from langchain_core.chat_history import BaseChatMessageHistory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder


def summarize_history(history: BaseChatMessageHistory, llm: LLMModel = LLMModel):
    if not history.messages:
        return

    prompt = ChatPromptTemplate.from_messages(
        [
            MessagesPlaceholder(variable_name="chat_history"),
            (
                "human",
                "Summarize the above chat messages into a concise message, focusing on key points and relevant details that could be useful for future conversations. Exclude all introductions and extraneous information.",
            ),
        ]
    )

    chain = prompt | llm.get_chat_anthropic()
    summary = chain.invoke({"chat_history": history.messages})

    history.clear()
    history.add_user_message("Current conversation summary till now")
    history.add_message(summary)
