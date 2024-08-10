from app.db.graph_db import GraphDBDataAccess


def get_graphs(graph_db_dao: GraphDBDataAccess):
    result = graph_db_dao.get_graphs()

    # Initialize lists for nodes and relationships
    nodes = []
    relationships = []

    # Define a set to track node IDs and avoid duplicates
    node_ids = set()

    # Iterate over each item in the data
    for item in result:
        # add node
        node1 = {
            "id": item["n"]["id"],
            "labels": item["nodeLabels"][0],
            "description": item["n"].get("description", ""),
        }
        node2 = {
            "id": item["m"]["id"],
            "labels": item["relatedNodeLabels"][0],
            "description": item["m"].get("description", ""),
        }

        if node1["id"] not in node_ids:
            nodes.append(node1)
            node_ids.add(node1["id"])

        if node2["id"] not in node_ids:
            nodes.append(node2)
            node_ids.add(node2["id"])

        # Add relationship
        relationship = {
            "source": item["r"][0]["id"],
            "target": item["r"][2]["id"],
            "type": item["r"][1],
        }
        relationships.append(relationship)

    # Return the nodes and relationships
    return {"nodes": nodes, "relationships": relationships}
