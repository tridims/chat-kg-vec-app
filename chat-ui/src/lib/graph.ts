import { MultiDirectedGraph } from 'graphology';
import circular from "graphology-layout/circular";

interface Node {
  id: string;
  labels: string;
  description: string;
}

interface Relationship {
  source: string;
  target: string;
  type: string;
}

interface GraphData {
  nodes: Node[];
  relationships: Relationship[];
}

function jsonToMultiDirectedGraph(data: GraphData): MultiDirectedGraph {
  const graph = new MultiDirectedGraph();

  // Add nodes
  data.nodes.forEach(node => {
    graph.addNode(node.id, {
      label: node.labels,
      description: node.description,
      size: 25
    });
  });

  // Add edges
  data.relationships.forEach(rel => {
    graph.addEdge(rel.source, rel.target, {
      label: rel.type,
      weight: 10
    });
  });

  circular.assign(graph, { scale: 100 });

  return graph;
}

export default jsonToMultiDirectedGraph;