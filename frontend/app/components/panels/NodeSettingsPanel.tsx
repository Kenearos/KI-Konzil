"use client";

import { useEffect, useState } from "react";
import { X, Bot } from "lucide-react";
import { AgentNodeData, LLMModel } from "@/app/types/council";
import { useCouncilStore } from "@/app/store/council-store";

const MODELS: { value: LLMModel; label: string }[] = [
  { value: "claude-3-5-sonnet", label: "Claude 3.5 Sonnet" },
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "local", label: "Lokal" },
];

// Right-side panel shown when an AgentNode is selected
export function NodeSettingsPanel() {
  const selectedNodeId = useCouncilStore((s) => s.selectedNodeId);
  const nodes = useCouncilStore((s) => s.nodes);
  const updateNodeData = useCouncilStore((s) => s.updateNodeData);
  const selectNode = useCouncilStore((s) => s.selectNode);

  const node = nodes.find((n) => n.id === selectedNodeId);
  const data = node?.data as AgentNodeData | undefined;

  // Local draft to avoid re-renders on every keystroke
  const [draft, setDraft] = useState<AgentNodeData | null>(null);

  useEffect(() => {
    setDraft(data ?? null);
  }, [selectedNodeId, data]);

  if (!selectedNodeId || !draft) return null;

  const commit = (partial: Partial<AgentNodeData>) => {
    const updated = { ...draft, ...partial };
    setDraft(updated);
    updateNodeData(selectedNodeId, partial);
  };

  return (
    <aside className="w-72 flex-shrink-0 bg-white border-l border-slate-200 p-4 flex flex-col gap-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Bot size={16} className="text-indigo-600" />
        <h2 className="font-semibold text-slate-800 text-sm flex-1">
          Agent-Einstellungen
        </h2>
        <button
          onClick={() => selectNode(null)}
          className="text-slate-400 hover:text-slate-600"
        >
          <X size={16} />
        </button>
      </div>

      {/* Name */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-500">Name</label>
        <input
          type="text"
          value={draft.label}
          onChange={(e) => commit({ label: e.target.value })}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
      </div>

      {/* System Prompt */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-500">
          System-Prompt
        </label>
        <textarea
          value={draft.systemPrompt}
          onChange={(e) => commit({ systemPrompt: e.target.value })}
          rows={6}
          placeholder="Beschreibe die Rolle und das Verhalten dieses Agenten..."
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-indigo-300"
        />
      </div>

      {/* Model */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-500">Modell</label>
        <select
          value={draft.model}
          onChange={(e) => commit({ model: e.target.value as LLMModel })}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
        >
          {MODELS.map((m) => (
            <option key={m.value} value={m.value}>
              {m.label}
            </option>
          ))}
        </select>
      </div>

      {/* Tools */}
      <div className="flex flex-col gap-2">
        <label className="text-xs font-medium text-slate-500">Tools</label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={draft.tools.webSearch}
            onChange={(e) =>
              commit({ tools: { ...draft.tools, webSearch: e.target.checked } })
            }
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-300"
          />
          <span className="text-sm text-slate-700">Web-Suche (Tavily)</span>
        </label>

        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={draft.tools.pdfReader}
            onChange={(e) =>
              commit({ tools: { ...draft.tools, pdfReader: e.target.checked } })
            }
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-300"
          />
          <span className="text-sm text-slate-700">PDF-Leser</span>
        </label>
      </div>

      {/* Edge type info */}
      <div className="mt-auto rounded-lg bg-slate-50 p-3 text-xs text-slate-500 leading-relaxed">
        <strong className="text-slate-600">Tipp:</strong> Verbinde zwei Agenten
        mit einer Kante. Klicke danach auf die Kante, um sie als{" "}
        <em>bedingt</em> zu markieren und einen Routing-Wert einzugeben (z. B.{" "}
        <code className="bg-slate-200 px-1 rounded">rework</code> oder{" "}
        <code className="bg-slate-200 px-1 rounded">approve</code>).
      </div>
    </aside>
  );
}
