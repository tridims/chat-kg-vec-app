import time
from langchain_community.graphs import Neo4jGraph
from src.qa_processor import QA_RAG_Vector_Graph
from dotenv import load_dotenv

load_dotenv()

question = "Which nation had to look on helpless sorrow because Germany, Italy, Spain and Belgium? And what did these nations do?"
session = 1

try:
    start_time = time.time()

    graph = Neo4jGraph(sanitize=True)
    result = QA_RAG_Vector_Graph(graph=graph, question=question, session_id=session)

    total_time = time.time() - start_time
    print(f"Total Response time is  {total_time:.2f} seconds")

    print(result)

except Exception as e:
    print(f"Error: {e}")
