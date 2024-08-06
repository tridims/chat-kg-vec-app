from dotenv import load_dotenv
from extractor import extract_graph_from_local_file
from graph_db import GraphDBDataAccess
from models import SourceNode
from langchain_community.graphs import Neo4jGraph

load_dotenv()

obj_source_node = SourceNode()
obj_source_node.file_name = "The King in Yellow.pdf"

graph = Neo4jGraph()

data_access = GraphDBDataAccess(graph)
data_access.create_source_node(obj_source_node)

file_path = "data/The King in Yellow.pdf"
local_file_result = extract_graph_from_local_file(
    graph, file_path, "The King in Yellow.pdf"
)

print(local_file_result)
