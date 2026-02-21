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
export type RunStatus = "pending" | "running" | "completed" | "failed" | "paused";

export type ExecutionMode = "auto-pilot" | "god-mode";

export interface CouncilRun {
  run_id: string;
  status: RunStatus;
  current_node?: string;
  result?: string;
  error?: string;
}

// God Mode state from the backend
export interface GodModeState {
  run_id: string;
  paused: boolean;
  next_nodes: string[];
  current_state: {
    current_draft?: string;
    critic_score?: number;
    iteration_count?: number;
    feedback_history?: string[];
  };
}

export type GodModeAction = "approve" | "reject" | "modify";

// WebSocket messages from backend
export type WSEventType =
  | "connected"
  | "node_active"
  | "run_paused"
  | "run_resumed"
  | "run_complete"
  | "run_failed";

export interface WSMessage {
  event: WSEventType;
  run_id: string;
  // node_active
  node?: string;
  iteration?: number;
  // run_paused
  next_nodes?: string[];
  current_draft?: string;
  critic_score?: number;
  iteration_count?: number;
  // run_complete
  final_draft?: string;
  // run_failed
  error?: string;
}
