// Parser: React Flow graph state → CouncilBlueprint JSON (backend format)
import { Node, Edge } from "@xyflow/react";
import { AgentNodeData, BlueprintEdge, BlueprintNode, CouncilBlueprint, EdgeType } from "@/app/types/council";

export function parseGraphToBlueprint(
  nodes: Node<AgentNodeData>[],
  edges: Edge[],
  name: string,
  existingId?: string
): CouncilBlueprint {
  const blueprintNodes: BlueprintNode[] = nodes.map((node) => ({
    id: node.id,
    label: node.data.label,
    systemPrompt: node.data.systemPrompt,
    model: node.data.model,
    tools: node.data.tools,
    position: { x: node.position.x, y: node.position.y },
  }));

  const blueprintEdges: BlueprintEdge[] = edges.map((edge) => {
    const edgeType: EdgeType = (edge.data?.type as EdgeType) ?? "linear";
    const result: BlueprintEdge = {
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edgeType,
    };
    if (edgeType === "conditional" && edge.data?.condition) {
      result.condition = edge.data.condition as string;
    }
    return result;
  });

  return {
    version: 1,
    id: existingId,
    name,
    nodes: blueprintNodes,
    edges: blueprintEdges,
  };
}

// Reverse: CouncilBlueprint → React Flow nodes/edges (for loading saved blueprints)
export function parseBlueprintToGraph(blueprint: CouncilBlueprint): {
  nodes: Node<AgentNodeData>[];
  edges: Edge[];
} {
  const nodes: Node<AgentNodeData>[] = blueprint.nodes.map((n) => ({
    id: n.id,
    type: "agentNode",
    position: n.position,
    data: {
      label: n.label,
      systemPrompt: n.systemPrompt,
      model: n.model,
      tools: n.tools,
    },
  }));

  const edges: Edge[] = blueprint.edges.map((e) => ({
    id: e.id,
    source: e.source,
    target: e.target,
    type: e.type === "conditional" ? "conditionalEdge" : "default",
    data: { type: e.type, condition: e.condition },
    label: e.type === "conditional" ? e.condition : undefined,
    animated: e.type === "conditional",
  }));

  return { nodes, edges };
}
