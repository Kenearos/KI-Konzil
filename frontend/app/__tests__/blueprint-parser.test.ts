import { describe, it, expect } from "vitest";
import { parseGraphToBlueprint, parseBlueprintToGraph } from "@/app/utils/blueprint-parser";
import { Node, Edge } from "@xyflow/react";
import { AgentNodeData, CouncilBlueprint } from "@/app/types/council";

describe("parseGraphToBlueprint", () => {
  it("should convert React Flow nodes and edges to blueprint format", () => {
    const nodes: Node<AgentNodeData>[] = [
      {
        id: "n1",
        type: "agentNode",
        position: { x: 100, y: 200 },
        data: {
          label: "Master Agent",
          systemPrompt: "You are the master writer.",
          model: "claude-3-5-sonnet",
          tools: { webSearch: true, pdfReader: false },
        },
      },
      {
        id: "n2",
        type: "agentNode",
        position: { x: 400, y: 200 },
        data: {
          label: "Critic Agent",
          systemPrompt: "You evaluate drafts.",
          model: "gpt-4o",
          tools: { webSearch: false, pdfReader: true },
        },
      },
    ];

    const edges: Edge[] = [
      {
        id: "e1",
        source: "n1",
        target: "n2",
        type: "default",
        data: { type: "linear" },
      },
    ];

    const blueprint = parseGraphToBlueprint(nodes, edges, "Test Council");

    expect(blueprint.version).toBe(1);
    expect(blueprint.name).toBe("Test Council");
    expect(blueprint.nodes).toHaveLength(2);
    expect(blueprint.edges).toHaveLength(1);

    expect(blueprint.nodes[0].label).toBe("Master Agent");
    expect(blueprint.nodes[0].tools.webSearch).toBe(true);
    expect(blueprint.nodes[1].model).toBe("gpt-4o");

    expect(blueprint.edges[0].type).toBe("linear");
    expect(blueprint.edges[0].source).toBe("n1");
    expect(blueprint.edges[0].target).toBe("n2");
  });

  it("should handle conditional edges with condition labels", () => {
    const nodes: Node<AgentNodeData>[] = [
      {
        id: "n1",
        type: "agentNode",
        position: { x: 0, y: 0 },
        data: {
          label: "A",
          systemPrompt: "",
          model: "claude-3-5-sonnet",
          tools: { webSearch: false, pdfReader: false },
        },
      },
    ];

    const edges: Edge[] = [
      {
        id: "e1",
        source: "n1",
        target: "n2",
        type: "conditionalEdge",
        data: { type: "conditional", condition: "approve" },
      },
    ];

    const blueprint = parseGraphToBlueprint(nodes, edges, "Test");
    expect(blueprint.edges[0].type).toBe("conditional");
    expect(blueprint.edges[0].condition).toBe("approve");
  });

  it("should preserve existing blueprint ID", () => {
    const blueprint = parseGraphToBlueprint([], [], "Test", "existing-id");
    expect(blueprint.id).toBe("existing-id");
  });
});

describe("parseBlueprintToGraph", () => {
  it("should convert blueprint back to React Flow format", () => {
    const blueprint: CouncilBlueprint = {
      version: 1,
      name: "Test",
      nodes: [
        {
          id: "n1",
          label: "Master",
          systemPrompt: "You are the master.",
          model: "claude-3-5-sonnet",
          tools: { webSearch: true, pdfReader: false },
          position: { x: 100, y: 200 },
        },
      ],
      edges: [
        {
          id: "e1",
          source: "n1",
          target: "n2",
          type: "conditional",
          condition: "rework",
        },
      ],
    };

    const { nodes, edges } = parseBlueprintToGraph(blueprint);

    expect(nodes).toHaveLength(1);
    expect(nodes[0].type).toBe("agentNode");
    expect(nodes[0].data.label).toBe("Master");
    expect(nodes[0].data.tools.webSearch).toBe(true);

    expect(edges).toHaveLength(1);
    expect(edges[0].type).toBe("conditionalEdge");
    expect(edges[0].data?.condition).toBe("rework");
    expect(edges[0].animated).toBe(true);
  });

  it("should handle linear edges", () => {
    const blueprint: CouncilBlueprint = {
      version: 1,
      name: "Test",
      nodes: [],
      edges: [
        { id: "e1", source: "a", target: "b", type: "linear" },
      ],
    };

    const { edges } = parseBlueprintToGraph(blueprint);
    expect(edges[0].type).toBe("default");
    expect(edges[0].animated).toBe(false);
  });
});
