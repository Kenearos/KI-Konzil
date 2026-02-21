// Zustand store for canvas state and council run state
import { create } from "zustand";
import { Node, Edge, addEdge, applyNodeChanges, applyEdgeChanges, NodeChange, EdgeChange, Connection } from "@xyflow/react";
import { AgentNodeData, CouncilRun, EdgeType } from "@/app/types/council";
import { nanoid } from "nanoid";

interface CouncilStore {
  // Canvas
  nodes: Node<AgentNodeData>[];
  edges: Edge[];
  selectedNodeId: string | null;
  selectedEdgeId: string | null;
  councilName: string;

  // Execution
  activeRun: CouncilRun | null;
  activeNodeId: string | null;

  // Canvas actions
  onNodesChange: (changes: NodeChange[]) => void;
  onEdgesChange: (changes: EdgeChange[]) => void;
  onConnect: (connection: Connection) => void;
  addAgentNode: (position: { x: number; y: number }) => void;
  updateNodeData: (nodeId: string, data: Partial<AgentNodeData>) => void;
  selectNode: (nodeId: string | null) => void;
  selectEdge: (edgeId: string | null) => void;
  updateEdgeData: (edgeId: string, type: EdgeType, condition?: string) => void;
  setCouncilName: (name: string) => void;
  setNodes: (nodes: Node<AgentNodeData>[]) => void;
  setEdges: (edges: Edge[]) => void;

  // Run actions
  setActiveRun: (run: CouncilRun | null) => void;
  setActiveNodeId: (nodeId: string | null) => void;
  markNodeActive: (nodeName: string) => void;
  clearActiveNode: () => void;
}

function makeDefaultNodeData(label: string): AgentNodeData {
  return {
    label,
    systemPrompt: "",
    model: "claude-3-5-sonnet",
    tools: { webSearch: false, pdfReader: false },
    isActive: false,
  };
}

export const useCouncilStore = create<CouncilStore>((set, get) => ({
  nodes: [],
  edges: [],
  selectedNodeId: null,
  selectedEdgeId: null,
  councilName: "Mein Rat",
  activeRun: null,
  activeNodeId: null,

  onNodesChange: (changes) =>
    set((state) => ({
      nodes: applyNodeChanges(changes, state.nodes) as Node<AgentNodeData>[],
    })),

  onEdgesChange: (changes) =>
    set((state) => ({
      edges: applyEdgeChanges(changes, state.edges),
    })),

  onConnect: (connection) =>
    set((state) => ({
      edges: addEdge(
        { ...connection, type: "default", data: { type: "linear" } },
        state.edges
      ),
    })),

  addAgentNode: (position) => {
    const id = nanoid();
    const count = get().nodes.length + 1;
    const newNode: Node<AgentNodeData> = {
      id,
      type: "agentNode",
      position,
      data: makeDefaultNodeData(`Agent ${count}`),
    };
    set((state) => ({ nodes: [...state.nodes, newNode] }));
  },

  updateNodeData: (nodeId, data) =>
    set((state) => ({
      nodes: state.nodes.map((n) =>
        n.id === nodeId ? { ...n, data: { ...n.data, ...data } } : n
      ),
    })),

  selectNode: (nodeId) => set({ selectedNodeId: nodeId, selectedEdgeId: null }),

  selectEdge: (edgeId) => set({ selectedEdgeId: edgeId, selectedNodeId: null }),

  updateEdgeData: (edgeId, type, condition) =>
    set((state) => ({
      edges: state.edges.map((e) =>
        e.id === edgeId
          ? {
              ...e,
              type: type === "conditional" ? "conditionalEdge" : "default",
              data: { ...e.data, type, condition: condition ?? "" },
              label: type === "conditional" ? (condition || "?") : undefined,
              animated: type === "conditional",
            }
          : e
      ),
    })),

  setCouncilName: (name) => set({ councilName: name }),

  setNodes: (nodes) => set({ nodes }),

  setEdges: (edges) => set({ edges }),

  setActiveRun: (run) => set({ activeRun: run }),

  setActiveNodeId: (nodeId) => set({ activeNodeId: nodeId }),

  markNodeActive: (nodeName) => {
    const node = get().nodes.find((n) => n.data.label === nodeName);
    if (node) {
      set((state) => ({
        activeNodeId: node.id,
        nodes: state.nodes.map((n) => ({
          ...n,
          data: { ...n.data, isActive: n.id === node.id },
        })),
      }));
    }
  },

  clearActiveNode: () =>
    set((state) => ({
      activeNodeId: null,
      nodes: state.nodes.map((n) => ({
        ...n,
        data: { ...n.data, isActive: false },
      })),
    })),
}));
