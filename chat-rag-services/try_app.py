from langchain_community.graphs import Neo4jGraph
from dotenv import load_dotenv

from src.controller import get_chat_completions
from src.processor.completions import QAEngine

load_dotenv()

question = "Which nation had to look on helpless sorrow because Germany, Italy, Spain and Belgium? And what did these nations do?"
session = "dimas"

engine = QAEngine(Neo4jGraph(sanitize=True))


result = get_chat_completions(engine, question, session)

print(result)
