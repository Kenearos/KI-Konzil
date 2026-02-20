// Council blueprint types — canonical exchange format between frontend and backend
// Version field allows schema evolution

export type LLMModel = "claude-3-5-sonnet" | "gpt-4o" | "local";

export interface AgentTools {
  webSearch: boolean;
  pdfReader: boolean;
}

export interface AgentNodeData extends Record<string, unknown> {
  label: string;
  systemPrompt: string;
  model: LLMModel;
  tools: AgentTools;
  isActive?: boolean; // set by WebSocket during execution
}

export type EdgeType = "linear" | "conditional";

export interface ConditionalEdgeData {
  condition: string; // e.g. "rework" | "approve"
}

// Blueprint JSON — versioned, stored in PostgreSQL
export interface BlueprintNode {
  id: string;
  label: string;
  systemPrompt: string;
  model: LLMModel;
  tools: AgentTools;
  position: { x: number; y: number };
}

export interface BlueprintEdge {
  id: string;
  source: string;
  target: string;
  type: EdgeType;
  condition?: string;
}

export interface CouncilBlueprint {
  version: 1;
  id?: string;
  name: string;
  nodes: BlueprintNode[];
  edges: BlueprintEdge[];
  createdAt?: string;
  updatedAt?: string;
}

// Council run (execution)
export type RunStatus = "pending" | "running" | "completed" | "failed";

export interface CouncilRun {
  run_id: string;
  status: RunStatus;
  current_node?: string;
  result?: string;
  error?: string;
}

// WebSocket messages from backend
export type WSMessageType = "node_enter" | "node_exit" | "run_complete" | "run_error";

export interface WSMessage {
  type: WSMessageType;
  node_id?: string;
  node_name?: string;
  result?: string;
  error?: string;
}
