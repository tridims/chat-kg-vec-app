import "@react-sigma/core/lib/react-sigma.min.css";
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import { useEffect, useState } from "react";
import { MultiDirectedGraph } from "graphology";
import { useWorkerLayoutForceAtlas2 } from "@react-sigma/layout-forceatlas2";
import dummyGraph from "@/lib/graphs/dummy";

const sigmaStyle = { height: "100%", width: "100%" };

interface LoadGraphProps {
  graphData: MultiDirectedGraph;
}

// Component that loads the graph
export const LoadGraph = ({ graphData }: LoadGraphProps) => {
  const loadGraph = useLoadGraph();

  useEffect(() => {
    loadGraph(graphData);
  }, [loadGraph, graphData]);

  return null;
};

// Component that manages the worker layout
const WorkerLayout = () => {
  const { start, kill } = useWorkerLayoutForceAtlas2({
    settings: { slowDown: 150, gravity: 1 },
  });

  useEffect(() => {
    // Start ForceAtlas2 layout
    start();

    // Kill ForceAtlas2 layout on unmount
    return () => {
      kill();
    };
  }, [start, kill]);

  return null;
};

// Component that displays the graph with worker layout
const DisplayGraphWithWorkerLayout = () => {
  const [graphData, setGraphData] = useState(dummyGraph);

  // Function to add a new node
  const addNode = (
    id: string,
    label: string,
    x: number,
    y: number,
    size: number,
    color: string
  ) => {
    setGraphData((prevGraph) => {
      const newGraph = prevGraph.copy(); // Clone the existing graph
      newGraph.addNode(id, { label, x, y, size, color }); // Add the new node to the cloned graph
      return newGraph; // Return the new graph instance
    });
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      addNode("newNode", "New Node Nodees", 10, 10, 20, "blue");
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  return (
    <SigmaContainer
      style={sigmaStyle}
      graph={MultiDirectedGraph}
      settings={{ allowInvalidContainer: true }}
    >
      <LoadGraph graphData={graphData} />
      <WorkerLayout />
    </SigmaContainer>
  );
};

export default DisplayGraphWithWorkerLayout;
