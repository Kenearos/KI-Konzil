import { describe, it, expect, beforeEach } from "vitest";
import { useCouncilStore } from "@/app/store/council-store";

describe("CouncilStore", () => {
  beforeEach(() => {
    // Reset store state between tests
    useCouncilStore.setState({
      nodes: [],
      edges: [],
      selectedNodeId: null,
      selectedEdgeId: null,
      councilName: "Mein Rat",
      activeRun: null,
      activeNodeId: null,
    });
  });

  it("should have default state", () => {
    const state = useCouncilStore.getState();
    expect(state.nodes).toEqual([]);
    expect(state.edges).toEqual([]);
    expect(state.selectedNodeId).toBeNull();
    expect(state.selectedEdgeId).toBeNull();
    expect(state.councilName).toBe("Mein Rat");
  });

  it("should add an agent node", () => {
    const { addAgentNode } = useCouncilStore.getState();
    addAgentNode({ x: 100, y: 200 });

    const { nodes } = useCouncilStore.getState();
    expect(nodes).toHaveLength(1);
    expect(nodes[0].position).toEqual({ x: 100, y: 200 });
    expect(nodes[0].type).toBe("agentNode");
    expect(nodes[0].data.label).toBe("Agent 1");
    expect(nodes[0].data.model).toBe("claude-3-5-sonnet");
    expect(nodes[0].data.tools).toEqual({ webSearch: false, pdfReader: false });
  });

  it("should update node data", () => {
    const { addAgentNode } = useCouncilStore.getState();
    addAgentNode({ x: 0, y: 0 });

    const { nodes, updateNodeData } = useCouncilStore.getState();
    const nodeId = nodes[0].id;

    updateNodeData(nodeId, { label: "Master Agent", model: "gpt-4o" });

    const updated = useCouncilStore.getState().nodes[0];
    expect(updated.data.label).toBe("Master Agent");
    expect(updated.data.model).toBe("gpt-4o");
  });

  it("should select a node and deselect edge", () => {
    const { selectNode } = useCouncilStore.getState();
    selectNode("node-1");

    const state = useCouncilStore.getState();
    expect(state.selectedNodeId).toBe("node-1");
    expect(state.selectedEdgeId).toBeNull();
  });

  it("should select an edge and deselect node", () => {
    const { selectEdge, selectNode } = useCouncilStore.getState();
    selectNode("node-1");
    selectEdge("edge-1");

    const state = useCouncilStore.getState();
    expect(state.selectedEdgeId).toBe("edge-1");
    expect(state.selectedNodeId).toBeNull();
  });

  it("should update edge data to conditional", () => {
    useCouncilStore.setState({
      edges: [
        {
          id: "e1",
          source: "a",
          target: "b",
          type: "default",
          data: { type: "linear" },
        },
      ],
    });

    const { updateEdgeData } = useCouncilStore.getState();
    updateEdgeData("e1", "conditional", "rework");

    const { edges } = useCouncilStore.getState();
    expect(edges[0].type).toBe("conditionalEdge");
    expect(edges[0].data?.type).toBe("conditional");
    expect(edges[0].data?.condition).toBe("rework");
    expect(edges[0].animated).toBe(true);
  });

  it("should update edge data back to linear", () => {
    useCouncilStore.setState({
      edges: [
        {
          id: "e1",
          source: "a",
          target: "b",
          type: "conditionalEdge",
          data: { type: "conditional", condition: "approve" },
          animated: true,
        },
      ],
    });

    const { updateEdgeData } = useCouncilStore.getState();
    updateEdgeData("e1", "linear");

    const { edges } = useCouncilStore.getState();
    expect(edges[0].type).toBe("default");
    expect(edges[0].data?.type).toBe("linear");
    expect(edges[0].animated).toBe(false);
  });

  it("should mark a node as active by name", () => {
    useCouncilStore.setState({
      nodes: [
        {
          id: "n1",
          type: "agentNode",
          position: { x: 0, y: 0 },
          data: {
            label: "Master Agent",
            systemPrompt: "",
            model: "claude-3-5-sonnet" as const,
            tools: { webSearch: false, pdfReader: false },
            isActive: false,
          },
        },
      ],
    });

    const { markNodeActive } = useCouncilStore.getState();
    markNodeActive("Master Agent");

    const { nodes, activeNodeId } = useCouncilStore.getState();
    expect(activeNodeId).toBe("n1");
    expect(nodes[0].data.isActive).toBe(true);
  });

  it("should clear active node", () => {
    useCouncilStore.setState({
      activeNodeId: "n1",
      nodes: [
        {
          id: "n1",
          type: "agentNode",
          position: { x: 0, y: 0 },
          data: {
            label: "Test",
            systemPrompt: "",
            model: "claude-3-5-sonnet" as const,
            tools: { webSearch: false, pdfReader: false },
            isActive: true,
          },
        },
      ],
    });

    const { clearActiveNode } = useCouncilStore.getState();
    clearActiveNode();

    const { nodes, activeNodeId } = useCouncilStore.getState();
    expect(activeNodeId).toBeNull();
    expect(nodes[0].data.isActive).toBe(false);
  });

  it("should set council name", () => {
    const { setCouncilName } = useCouncilStore.getState();
    setCouncilName("Test Rat");

    expect(useCouncilStore.getState().councilName).toBe("Test Rat");
  });
});
