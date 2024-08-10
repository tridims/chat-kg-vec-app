from langchain.chains import GraphCypherQAChain
from app.db.llm import LLMModel


def create_graph_chain(graph):
    cypher_llm = LLMModel.get_chat_anthropic()
    qa_llm = LLMModel.get_chat_anthropic()
    graph_chain = GraphCypherQAChain.from_llm(
        cypher_llm=cypher_llm,
        qa_llm=qa_llm,
        validate_cypher=True,
        graph=graph,
        return_intermediate_steps=True,
        top_k=3,
    )

    return graph_chain, qa_llm


def get_graph_response(graph_chain, question):
    cypher_res = graph_chain.invoke({"query": question})

    response = cypher_res.get("result")
    cypher_query = ""
    context = []

    for step in cypher_res.get("intermediate_steps", []):
        if "query" in step:
            cypher_string = step["query"]
            cypher_query = (
                cypher_string.replace("cypher\n", "").replace("\n", " ").strip()
            )
        elif "context" in step:
            context = step["context"]
    return {"response": response, "cypher_query": cypher_query, "context": context}
