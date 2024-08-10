// import { RotateCw } from "lucide-react";
// import { Button } from "./ui/button";
import dynamic from "next/dynamic";

const DisplayGraph = dynamic(() => import("./DisplayGraph"), {
  ssr: false,
  loading: () => <p>Loading graph...</p>,
});

export function GraphUI() {
  return (
    <div className="flex h-full flex-col">
      <header className="sticky top-0 z-10 border-b bg-background px-6 py-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium">Graph Visualization</h3>
          {/* <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon">
              <RotateCw className="h-5 w-5" />
            </Button>
          </div> */}
        </div>
      </header>
      <div className="flex-1 overflow-auto p-6">
        {/* <Graph className="w-full aspect-[4/3]" /> */}
        <DisplayGraph />
      </div>
    </div>
  );
}
