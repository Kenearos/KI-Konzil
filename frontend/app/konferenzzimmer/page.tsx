"use client";

import { useState, useCallback } from "react";
import { ReactFlowProvider } from "@xyflow/react";
import { Play, Square, Upload } from "lucide-react";
import { ArchitectCanvas } from "@/app/components/ArchitectCanvas";
import { useCouncilWebSocket } from "@/app/hooks/useCouncilWebSocket";
import { useCouncilStore } from "@/app/store/council-store";
import { runApi } from "@/app/utils/api-client";

export default function KonferenzzimmerPage() {
  const [topic, setTopic] = useState("");
  const [runId, setRunId] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const setActiveRun = useCouncilStore((s) => s.setActiveRun);
  const clearActiveNode = useCouncilStore((s) => s.clearActiveNode);

  const onComplete = useCallback((res: string) => {
    setResult(res);
    setIsRunning(false);
    setRunId(null);
  }, []);

  const onError = useCallback((err: string) => {
    setError(err);
    setIsRunning(false);
    setRunId(null);
  }, []);

  useCouncilWebSocket({ run_id: runId, onComplete, onError });

  const handleStart = async () => {
    if (!topic.trim()) return;
    setResult(null);
    setError(null);
    setIsRunning(true);
    clearActiveNode();
    try {
      const run = await runApi.start(topic);
      setActiveRun(run);
      setRunId(run.run_id);
    } catch (e) {
      setError("Fehler beim Starten: " + (e as Error).message);
      setIsRunning(false);
    }
  };

  const handleStop = () => {
    setRunId(null);
    setIsRunning(false);
    clearActiveNode();
    setActiveRun(null);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Control bar */}
      <header className="flex items-center gap-3 px-4 py-2 border-b border-slate-200 bg-white flex-shrink-0">
        <textarea
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Thema oder Aufgabe eingeben..."
          rows={1}
          className="flex-1 rounded-lg border border-slate-200 px-3 py-1.5 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
        <button className="flex items-center gap-1.5 text-sm text-slate-600 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors">
          <Upload size={14} />
          PDF
        </button>
        {!isRunning ? (
          <button
            onClick={handleStart}
            disabled={!topic.trim()}
            className="flex items-center gap-1.5 text-sm text-white bg-indigo-600 px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <Play size={14} />
            Start
          </button>
        ) : (
          <button
            onClick={handleStop}
            className="flex items-center gap-1.5 text-sm text-white bg-red-500 px-3 py-1.5 rounded-lg hover:bg-red-600 transition-colors"
          >
            <Square size={14} />
            Stopp
          </button>
        )}
      </header>

      {/* Canvas (read-only, agent nodes pulse when active) */}
      <div className="flex flex-1 overflow-hidden">
        <ReactFlowProvider>
          <div className="flex-1 h-full relative">
            <ArchitectCanvas />
            {isRunning && (
              <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-xs px-4 py-1.5 rounded-full shadow-lg animate-pulse pointer-events-none">
                Rat läuft…
              </div>
            )}
          </div>
        </ReactFlowProvider>

        {/* Output panel */}
        <aside className="w-80 flex-shrink-0 border-l border-slate-200 bg-white flex flex-col">
          <div className="px-4 py-3 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-700">Ergebnis</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4">
            {error && (
              <div className="rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                {error}
              </div>
            )}
            {result && (
              <div className="rounded-lg bg-slate-50 border border-slate-200 p-3 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
                {result}
              </div>
            )}
            {!result && !error && !isRunning && (
              <p className="text-sm text-slate-400 italic">
                Noch kein Ergebnis. Starte den Rat mit einem Thema.
              </p>
            )}
            {isRunning && !result && (
              <div className="space-y-2">
                {[1, 2, 3].map((i) => (
                  <div
                    key={i}
                    className="h-3 bg-slate-100 rounded animate-pulse"
                    style={{ width: `${70 + i * 10}%` }}
                  />
                ))}
              </div>
            )}
          </div>
        </aside>
      </div>
    </div>
  );
}
