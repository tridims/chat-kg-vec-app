import "@react-sigma/core/lib/react-sigma.min.css";
import { SigmaContainer, useLoadGraph } from "@react-sigma/core";
import { useEffect, useState } from "react";
import { MultiDirectedGraph } from "graphology";
import { useLayoutCircular } from "@react-sigma/layout-circular";
import { useLayoutForceAtlas2 } from "@react-sigma/layout-forceatlas2";
import jsonToMultiDirectedGraph from "@/lib/graph";

const sigmaStyle = { height: "100%", width: "100%" };

interface LoadGraphProps {
  graphData: MultiDirectedGraph;
}

// Component that loads the graph
const LoadGraph = ({ graphData }: LoadGraphProps) => {
  const loadGraph = useLoadGraph();
  const { positions, assign } = useLayoutCircular();

  useEffect(() => {
    const graph = loadGraph(graphData);
    assign();
  }, [loadGraph, assign, graphData]);

  return null;
};

// Component that displays the graph
const DisplayGraph = () => {
  const [graphData, setGraphData] = useState<MultiDirectedGraph | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch("http://localhost:8000/graph");
        const data = await response.json();
        const parsedGraph = jsonToMultiDirectedGraph(data);
        setGraphData(parsedGraph);
      } catch (error) {
        console.error("Error fetching graph data:", error);
      }
    };

    // Fetch data immediately
    fetchData();

    // Set up interval to fetch data every 5 seconds
    const intervalId = setInterval(fetchData, 2000);

    // Clean up interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  if (!graphData) {
    return <div>Loading...</div>;
  }

  return (
    <SigmaContainer style={sigmaStyle} graph={MultiDirectedGraph}>
      <LoadGraph graphData={graphData} />
    </SigmaContainer>
  );
};

export default DisplayGraph;
