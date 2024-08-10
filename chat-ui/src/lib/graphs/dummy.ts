import { MultiDirectedGraph } from "graphology";
import circular from "graphology-layout/circular";

const graph = new MultiDirectedGraph();

const dummyGraphData = {
  nodes: [
    { id: "New York", label: "New York", attributes: { color: "red", size: 10 } },
    { id: "Los Angeles", label: "Los Angeles", attributes: { color: "blue", size: 20 } },
    { id: "Chicago", label: "Chicago", attributes: { color: "green", size: 30 } },
    { id: "Houston", label: "Houston", attributes: { color: "purple", size: 25 } },
    { id: "Phoenix", label: "Phoenix", attributes: { color: "orange", size: 15 } },
    { id: "Philadelphia", label: "Philadelphia", attributes: { color: "yellow", size: 18 } },
    { id: "San Antonio", label: "San Antonio", attributes: { color: "pink", size: 22 } },
    { id: "San Diego", label: "San Diego", attributes: { color: "cyan", size: 12 } },
    { id: "Dallas", label: "Dallas", attributes: { color: "magenta", size: 28 } },
    { id: "San Jose", label: "San Jose", attributes: { color: "lime", size: 16 } },
  ],
  edges: [
    { source: "New York", target: "Los Angeles", attributes: { weight: 5 } },
    { source: "Los Angeles", target: "Chicago", attributes: { weight: 10 } },
    { source: "Chicago", target: "New York", attributes: { weight: 15 } },
    { source: "Houston", target: "Phoenix", attributes: { weight: 8 } },
    { source: "Phoenix", target: "Philadelphia", attributes: { weight: 12 } },
    { source: "Philadelphia", target: "San Antonio", attributes: { weight: 7 } },
    { source: "San Antonio", target: "San Diego", attributes: { weight: 9 } },
    { source: "San Diego", target: "Dallas", attributes: { weight: 11 } },
    { source: "Dallas", target: "San Jose", attributes: { weight: 6 } },
    { source: "San Jose", target: "New York", attributes: { weight: 13 } },
    { source: "New York", target: "Houston", attributes: { weight: 14 } },
    { source: "Los Angeles", target: "Phoenix", attributes: { weight: 4 } },
    { source: "Chicago", target: "Philadelphia", attributes: { weight: 3 } },
    { source: "Houston", target: "San Antonio", attributes: { weight: 2 } },
    { source: "Phoenix", target: "San Diego", attributes: { weight: 1 } },
  ],
};

dummyGraphData.nodes.forEach((node) => {
  graph.addNode(node.id, {
    label: node.label,
    color: node.attributes.color,
    size: node.attributes.size,
  });
});

dummyGraphData.edges.forEach((edge) => {
  graph.addEdge(edge.source, edge.target, {
    weight: edge.attributes.weight,
  });
});

// Apply circular layout
circular.assign(graph, { scale: 100 });

export default graph;