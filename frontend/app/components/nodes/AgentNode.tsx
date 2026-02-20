"use client";

import { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Bot, Globe, FileText } from "lucide-react";
import { AgentNodeData } from "@/app/types/council";
import { useCouncilStore } from "@/app/store/council-store";

const MODEL_LABELS: Record<string, string> = {
  "claude-3-5-sonnet": "Claude 3.5",
  "gpt-4o": "GPT-4o",
  local: "Lokal",
};

const MODEL_COLORS: Record<string, string> = {
  "claude-3-5-sonnet": "bg-orange-100 text-orange-700 border-orange-300",
  "gpt-4o": "bg-green-100 text-green-700 border-green-300",
  local: "bg-gray-100 text-gray-700 border-gray-300",
};

export const AgentNode = memo(function AgentNode({
  id,
  data,
  selected,
}: NodeProps) {
  const nodeData = data as AgentNodeData;
  const selectNode = useCouncilStore((s) => s.selectNode);

  const isActive = nodeData.isActive;

  return (
    <div
      onClick={() => selectNode(id)}
      className={[
        "w-52 rounded-xl border-2 bg-white shadow-md transition-all duration-300 cursor-pointer",
        isActive
          ? "border-indigo-500 shadow-indigo-200 shadow-lg animate-pulse"
          : selected
          ? "border-indigo-400 shadow-indigo-100"
          : "border-slate-200 hover:border-slate-400",
      ].join(" ")}
    >
      {/* Header */}
      <div
        className={[
          "flex items-center gap-2 rounded-t-xl px-3 py-2",
          isActive ? "bg-indigo-50" : "bg-slate-50",
        ].join(" ")}
      >
        <Bot
          size={16}
          className={isActive ? "text-indigo-600" : "text-slate-500"}
        />
        <span className="font-semibold text-sm text-slate-800 truncate flex-1">
          {nodeData.label}
        </span>
        {isActive && (
          <span className="text-xs text-indigo-600 font-medium">aktiv</span>
        )}
      </div>

      {/* Body */}
      <div className="px-3 py-2 space-y-2">
        {/* System prompt preview */}
        <p className="text-xs text-slate-500 line-clamp-2 min-h-[2rem]">
          {nodeData.systemPrompt || (
            <span className="italic text-slate-300">Kein System-Prompt</span>
          )}
        </p>

        {/* Model badge */}
        <span
          className={[
            "inline-block text-xs px-2 py-0.5 rounded-full border font-medium",
            MODEL_COLORS[nodeData.model] ?? MODEL_COLORS["local"],
          ].join(" ")}
        >
          {MODEL_LABELS[nodeData.model] ?? nodeData.model}
        </span>

        {/* Tool toggles */}
        {(nodeData.tools.webSearch || nodeData.tools.pdfReader) && (
          <div className="flex gap-2">
            {nodeData.tools.webSearch && (
              <span className="flex items-center gap-1 text-xs text-blue-600 bg-blue-50 px-2 py-0.5 rounded-full">
                <Globe size={10} />
                Web
              </span>
            )}
            {nodeData.tools.pdfReader && (
              <span className="flex items-center gap-1 text-xs text-purple-600 bg-purple-50 px-2 py-0.5 rounded-full">
                <FileText size={10} />
                PDF
              </span>
            )}
          </div>
        )}
      </div>

      {/* Handles */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-3 !h-3 !bg-slate-400 !border-white !border-2"
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!w-3 !h-3 !bg-indigo-500 !border-white !border-2"
      />
    </div>
  );
});
