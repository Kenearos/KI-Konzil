import { describe, it, expect } from "vitest";
import type {
  AgentNodeData,
  ExecutionMode,
  GodModeAction,
  GodModeState,
  RunStatus,
  WSEventType,
  WSMessage,
} from "@/app/types/council";

describe("Council types", () => {
  it("should support all run statuses", () => {
    const statuses: RunStatus[] = ["pending", "running", "completed", "failed", "paused"];
    expect(statuses).toHaveLength(5);
  });

  it("should support execution modes", () => {
    const modes: ExecutionMode[] = ["auto-pilot", "god-mode"];
    expect(modes).toHaveLength(2);
  });

  it("should support god mode actions", () => {
    const actions: GodModeAction[] = ["approve", "reject", "modify"];
    expect(actions).toHaveLength(3);
  });

  it("should support all WS event types", () => {
    const events: WSEventType[] = [
      "connected",
      "node_active",
      "run_paused",
      "run_resumed",
      "run_complete",
      "run_failed",
    ];
    expect(events).toHaveLength(6);
  });

  it("should enforce AgentNodeData structure", () => {
    const data: AgentNodeData = {
      label: "Test Agent",
      systemPrompt: "You are a test agent.",
      model: "claude-3-5-sonnet",
      tools: { webSearch: true, pdfReader: false },
      isActive: false,
    };
    expect(data.label).toBe("Test Agent");
    expect(data.tools.webSearch).toBe(true);
  });

  it("should enforce GodModeState structure", () => {
    const state: GodModeState = {
      run_id: "test-run",
      paused: true,
      next_nodes: ["critic"],
      current_state: {
        current_draft: "Draft text",
        critic_score: 6.5,
        iteration_count: 2,
      },
    };
    expect(state.paused).toBe(true);
    expect(state.next_nodes).toContain("critic");
    expect(state.current_state.critic_score).toBe(6.5);
  });

  it("should enforce WSMessage structure", () => {
    const msg: WSMessage = {
      event: "run_paused",
      run_id: "test",
      next_nodes: ["agent1"],
      current_draft: "Draft",
      critic_score: 7.0,
    };
    expect(msg.event).toBe("run_paused");
    expect(msg.next_nodes).toHaveLength(1);
  });
});
