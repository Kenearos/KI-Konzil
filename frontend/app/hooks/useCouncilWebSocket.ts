"use client";

import { useEffect, useRef, useCallback } from "react";
import { WSMessage } from "@/app/types/council";
import { wsUrl } from "@/app/utils/api-client";
import { useCouncilStore } from "@/app/store/council-store";

interface Options {
  run_id: string | null;
  onComplete?: (result: string) => void;
  onError?: (error: string) => void;
}

// WebSocket hook for live agent status updates during a council run
export function useCouncilWebSocket({ run_id, onComplete, onError }: Options) {
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

      switch (msg.type) {
        case "node_enter":
          if (msg.node_name) markNodeActive(msg.node_name);
          break;
        case "node_exit":
          clearActiveNode();
          break;
        case "run_complete":
          clearActiveNode();
          setActiveRun(null);
          if (msg.result) onComplete?.(msg.result);
          disconnect();
          break;
        case "run_error":
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
