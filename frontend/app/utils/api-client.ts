// API client for the FastAPI backend
import { CouncilBlueprint, CouncilRun, GodModeAction, GodModeState } from "@/app/types/council";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

// Council blueprint CRUD
export const councilApi = {
  list: () => request<CouncilBlueprint[]>("/api/councils/"),

  get: (id: string) => request<CouncilBlueprint>(`/api/councils/${id}`),

  create: (blueprint: CouncilBlueprint) =>
    request<CouncilBlueprint>("/api/councils/", {
      method: "POST",
      body: JSON.stringify(blueprint),
    }),

  update: (id: string, blueprint: CouncilBlueprint) =>
    request<CouncilBlueprint>(`/api/councils/${id}`, {
      method: "PUT",
      body: JSON.stringify(blueprint),
    }),

  delete: (id: string) =>
    request<void>(`/api/councils/${id}`, { method: "DELETE" }),
};

// Council run (execution)
export const runApi = {
  start: (input_topic: string, god_mode: boolean = false) =>
    request<CouncilRun>("/api/councils/run", {
      method: "POST",
      body: JSON.stringify({ input_topic, god_mode }),
    }),

  startFromBlueprint: (blueprintId: string, input_topic: string, god_mode: boolean = false) =>
    request<CouncilRun>(`/api/councils/${blueprintId}/run`, {
      method: "POST",
      body: JSON.stringify({ input_topic, god_mode }),
    }),

  status: (run_id: string) =>
    request<CouncilRun>(`/api/councils/run/${run_id}`),

  // God Mode: approve/reject/modify a paused run
  approve: (run_id: string, action: GodModeAction, modified_state?: Record<string, unknown>) =>
    request<CouncilRun>(`/api/councils/run/${run_id}/approve`, {
      method: "POST",
      body: JSON.stringify({ action, modified_state }),
    }),

  // God Mode: get the paused state
  getState: (run_id: string) =>
    request<GodModeState>(`/api/councils/run/${run_id}/state`),
};

// PDF upload
export const pdfApi = {
  upload: async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${BASE_URL}/api/councils/upload-pdf`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) {
      const text = await res.text();
      throw new Error(`Upload error ${res.status}: ${text}`);
    }
    return res.json() as Promise<{ filename: string; chunks_ingested: number; message: string }>;
  },
};

// WebSocket URL helper
export function wsUrl(run_id: string): string {
  const wsBase = BASE_URL.replace(/^http/, "ws");
  return `${wsBase}/ws/council/${run_id}`;
}
