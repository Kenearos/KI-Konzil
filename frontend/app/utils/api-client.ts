// API client for the FastAPI backend
import { CouncilBlueprint, CouncilRun } from "@/app/types/council";

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
  start: (input_topic: string) =>
    request<CouncilRun>("/api/run", {
      method: "POST",
      body: JSON.stringify({ input_topic }),
    }),

  status: (run_id: string) =>
    request<CouncilRun>(`/api/run/${run_id}`),
};

// WebSocket URL helper
export function wsUrl(run_id: string): string {
  const wsBase = BASE_URL.replace(/^http/, "ws");
  return `${wsBase}/ws/council/${run_id}`;
}
