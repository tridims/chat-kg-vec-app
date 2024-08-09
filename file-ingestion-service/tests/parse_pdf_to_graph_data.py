from dotenv import load_dotenv
from src.models import SourceNode
from graph_db import GraphDBDataAccess
from controller import extract_graph
from langchain_community.graphs import Neo4jGraph

load_dotenv()

obj_source_node = SourceNode()
obj_source_node.file_name = "The King in Yellow.pdf"

graph = Neo4jGraph()

data_access = GraphDBDataAccess(graph)
data_access.add_document(obj_source_node)

file_path = "data/The King in Yellow.pdf"
local_file_result = extract_graph(graph, file_path, "The King in Yellow.pdf")

print(local_file_result)
