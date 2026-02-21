"use client";

import { useEffect, useRef, useCallback } from "react";
import { WSMessage } from "@/app/types/council";
import { wsUrl } from "@/app/utils/api-client";
import { useCouncilStore } from "@/app/store/council-store";

export interface PauseInfo {
  next_nodes: string[];
  current_draft: string;
  critic_score?: number;
  iteration_count?: number;
}

interface Options {
  run_id: string | null;
  onComplete?: (result: string) => void;
  onError?: (error: string) => void;
  onPaused?: (info: PauseInfo) => void;
  onResumed?: () => void;
}

// WebSocket hook for live agent status updates during a council run
export function useCouncilWebSocket({
  run_id,
  onComplete,
  onError,
  onPaused,
  onResumed,
}: Options) {
  const ws = useRef<WebSocket | null>(null);
  const markNodeActive = useCouncilStore((s) => s.markNodeActive);
  const clearActiveNode = useCouncilStore((s) => s.clearActiveNode);
  const setActiveRun = useCouncilStore((s) => s.setActiveRun);

  const disconnect = useCallback(() => {
    if (ws.current) {
      ws.current.close();
      ws.current = null;
    }
    clearActiveNode();
  }, [clearActiveNode]);

  useEffect(() => {
    if (!run_id) return;

    const socket = new WebSocket(wsUrl(run_id));
    ws.current = socket;

    socket.onmessage = (event: MessageEvent<string>) => {
      let msg: WSMessage;
      try {
        msg = JSON.parse(event.data) as WSMessage;
      } catch {
        return;
      }

      switch (msg.event) {
        case "node_active":
          if (msg.node) markNodeActive(msg.node);
          break;
        case "run_paused":
          clearActiveNode();
          onPaused?.({
            next_nodes: msg.next_nodes ?? [],
            current_draft: msg.current_draft ?? "",
            critic_score: msg.critic_score,
            iteration_count: msg.iteration_count,
          });
          break;
        case "run_resumed":
          onResumed?.();
          break;
        case "run_complete":
          clearActiveNode();
          setActiveRun(null);
          if (msg.final_draft) onComplete?.(msg.final_draft);
          disconnect();
          break;
        case "run_failed":
          clearActiveNode();
          setActiveRun(null);
          if (msg.error) onError?.(msg.error);
          disconnect();
          break;
      }
    };

    socket.onerror = () => {
      onError?.("WebSocket-Verbindungsfehler");
      disconnect();
    };

    return () => disconnect();
  }, [run_id]); // eslint-disable-line react-hooks/exhaustive-deps

  return { disconnect };
}
