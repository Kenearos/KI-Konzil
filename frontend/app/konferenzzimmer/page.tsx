"use client";

import { useState, useCallback, useRef } from "react";
import { ReactFlowProvider } from "@xyflow/react";
import { Play, Square, Upload, Shield, Zap } from "lucide-react";
import { ArchitectCanvas } from "@/app/components/ArchitectCanvas";
import { GodModePanel } from "@/app/components/panels/GodModePanel";
import { useCouncilWebSocket, PauseInfo } from "@/app/hooks/useCouncilWebSocket";
import { useCouncilStore } from "@/app/store/council-store";
import { runApi, pdfApi } from "@/app/utils/api-client";
import { ExecutionMode, GodModeAction } from "@/app/types/council";

export default function KonferenzzimmerPage() {
  const [topic, setTopic] = useState("");
  const [runId, setRunId] = useState<string | null>(null);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [executionMode, setExecutionMode] = useState<ExecutionMode>("auto-pilot");
  const [pauseInfo, setPauseInfo] = useState<PauseInfo | null>(null);
  const [isResuming, setIsResuming] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const setActiveRun = useCouncilStore((s) => s.setActiveRun);
  const clearActiveNode = useCouncilStore((s) => s.clearActiveNode);

  const onComplete = useCallback((res: string) => {
    setResult(res);
    setIsRunning(false);
    setRunId(null);
    setPauseInfo(null);
  }, []);

  const onError = useCallback((err: string) => {
    setError(err);
    setIsRunning(false);
    setRunId(null);
    setPauseInfo(null);
  }, []);

  const onPaused = useCallback((info: PauseInfo) => {
    setPauseInfo(info);
    setIsResuming(false);
  }, []);

  const onResumed = useCallback(() => {
    setPauseInfo(null);
    setIsResuming(false);
  }, []);

  useCouncilWebSocket({ run_id: runId, onComplete, onError, onPaused, onResumed });

  const handleStart = async () => {
    if (!topic.trim()) return;
    setResult(null);
    setError(null);
    setIsRunning(true);
    setPauseInfo(null);
    clearActiveNode();
    try {
      const godMode = executionMode === "god-mode";
      const run = await runApi.start(topic, godMode);
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
    setPauseInfo(null);
  };

  const handleGodModeAction = async (action: GodModeAction, modifiedDraft?: string) => {
    if (!runId) return;
    setIsResuming(true);

    try {
      const modified_state = modifiedDraft ? { current_draft: modifiedDraft } : undefined;
      await runApi.approve(runId, action, modified_state);

      if (action === "reject") {
        setError("Vom Benutzer im God Mode abgelehnt.");
        setIsRunning(false);
        setRunId(null);
        setPauseInfo(null);
      }
    } catch (e) {
      setError("Fehler bei God Mode Aktion: " + (e as Error).message);
      setIsResuming(false);
    }
  };

  const handlePdfUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    try {
      const res = await pdfApi.upload(file);
      setTopic((prev) =>
        prev
          ? `${prev}\n\n[PDF hochgeladen: ${res.filename} — ${res.chunks_ingested} Abschnitte]`
          : `[PDF hochgeladen: ${res.filename} — ${res.chunks_ingested} Abschnitte]`
      );
    } catch (e) {
      setError("PDF-Upload fehlgeschlagen: " + (e as Error).message);
    }
    // Reset the input
    if (fileInputRef.current) fileInputRef.current.value = "";
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

        {/* PDF upload */}
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf"
          onChange={handlePdfUpload}
          className="hidden"
        />
        <button
          onClick={() => fileInputRef.current?.click()}
          className="flex items-center gap-1.5 text-sm text-slate-600 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors"
        >
          <Upload size={14} />
          PDF
        </button>

        {/* Execution mode toggle */}
        <button
          onClick={() =>
            setExecutionMode((m) => (m === "auto-pilot" ? "god-mode" : "auto-pilot"))
          }
          disabled={isRunning}
          className={[
            "flex items-center gap-1.5 text-sm px-3 py-1.5 rounded-lg transition-colors border",
            executionMode === "god-mode"
              ? "bg-amber-50 text-amber-700 border-amber-300 hover:bg-amber-100"
              : "bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100",
            isRunning ? "opacity-50 cursor-not-allowed" : "",
          ].join(" ")}
          title={
            executionMode === "god-mode"
              ? "God Mode: Pause vor jedem Agenten"
              : "Auto-Pilot: Automatischer Durchlauf"
          }
        >
          {executionMode === "god-mode" ? (
            <Shield size={14} />
          ) : (
            <Zap size={14} />
          )}
          {executionMode === "god-mode" ? "God Mode" : "Auto-Pilot"}
        </button>

        {/* Start / Stop */}
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
            {isRunning && !pauseInfo && (
              <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white text-xs px-4 py-1.5 rounded-full shadow-lg animate-pulse pointer-events-none">
                Rat läuft…
              </div>
            )}
            {pauseInfo && (
              <div className="absolute top-3 left-1/2 -translate-x-1/2 bg-amber-500 text-white text-xs px-4 py-1.5 rounded-full shadow-lg pointer-events-none">
                Pausiert — Freigabe erforderlich
              </div>
            )}
          </div>
        </ReactFlowProvider>

        {/* Output panel */}
        <aside className="w-80 flex-shrink-0 border-l border-slate-200 bg-white flex flex-col">
          <div className="px-4 py-3 border-b border-slate-100">
            <h2 className="text-sm font-semibold text-slate-700">Ergebnis</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* God Mode approval panel */}
            {pauseInfo && (
              <GodModePanel
                pauseInfo={pauseInfo}
                onAction={handleGodModeAction}
                isResuming={isResuming}
              />
            )}

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
            {isRunning && !result && !pauseInfo && (
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
