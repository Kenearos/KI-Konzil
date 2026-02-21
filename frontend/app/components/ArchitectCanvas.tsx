"use client";

import { useCallback } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  BackgroundVariant,
  useReactFlow,
  Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import { AgentNode } from "@/app/components/nodes/AgentNode";
import { ConditionalEdge } from "@/app/components/edges/ConditionalEdge";
import { useCouncilStore } from "@/app/store/council-store";
import { AgentNodeData } from "@/app/types/council";

const NODE_TYPES = { agentNode: AgentNode };
const EDGE_TYPES = { conditionalEdge: ConditionalEdge };

// Main React Flow canvas — lives inside a ReactFlowProvider
export function ArchitectCanvas() {
  const nodes = useCouncilStore((s) => s.nodes);
  const edges = useCouncilStore((s) => s.edges);
  const onNodesChange = useCouncilStore((s) => s.onNodesChange);
  const onEdgesChange = useCouncilStore((s) => s.onEdgesChange);
  const onConnect = useCouncilStore((s) => s.onConnect);
  const addAgentNode = useCouncilStore((s) => s.addAgentNode);
  const selectNode = useCouncilStore((s) => s.selectNode);
  const selectEdge = useCouncilStore((s) => s.selectEdge);

  const { screenToFlowPosition } = useReactFlow();

  const onDragOver = useCallback((event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  }, []);

  const onDrop = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.preventDefault();
      const type = event.dataTransfer.getData("application/reactflow");
      if (type !== "agentNode") return;

      const position = screenToFlowPosition({
        x: event.clientX,
        y: event.clientY,
      });
      addAgentNode(position);
    },
    [screenToFlowPosition, addAgentNode]
  );

  const onPaneClick = useCallback(() => {
    selectNode(null);
    selectEdge(null);
  }, [selectNode, selectEdge]);

  const onEdgeClick = useCallback(
    (_event: React.MouseEvent, edge: Edge) => {
      selectEdge(edge.id);
    },
    [selectEdge]
  );

  return (
    <div className="flex-1 h-full">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onDrop={onDrop}
        onDragOver={onDragOver}
        onPaneClick={onPaneClick}
        onEdgeClick={onEdgeClick}
        nodeTypes={NODE_TYPES}
        edgeTypes={EDGE_TYPES}
        fitView
        deleteKeyCode="Delete"
        className="bg-slate-50"
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#cbd5e1" />
        <Controls />
        <MiniMap
          nodeColor={(n) => {
            const d = n.data as AgentNodeData;
            return d?.isActive ? "#6366f1" : "#94a3b8";
          }}
          className="!bg-white !border-slate-200"
        />
      </ReactFlow>
    </div>
  );
}
