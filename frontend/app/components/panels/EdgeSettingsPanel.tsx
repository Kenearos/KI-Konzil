"use client";

import { useEffect, useState } from "react";
import { X, ArrowRight } from "lucide-react";
import { EdgeType } from "@/app/types/council";
import { useCouncilStore } from "@/app/store/council-store";

// Right-side panel shown when a canvas edge is selected
export function EdgeSettingsPanel() {
  const selectedEdgeId = useCouncilStore((s) => s.selectedEdgeId);
  const edges = useCouncilStore((s) => s.edges);
  const nodes = useCouncilStore((s) => s.nodes);
  const updateEdgeData = useCouncilStore((s) => s.updateEdgeData);
  const selectEdge = useCouncilStore((s) => s.selectEdge);

  const edge = edges.find((e) => e.id === selectedEdgeId);

  const [edgeType, setEdgeType] = useState<EdgeType>("linear");
  const [condition, setCondition] = useState("");

  useEffect(() => {
    if (edge) {
      setEdgeType((edge.data?.type as EdgeType) ?? "linear");
      setCondition((edge.data?.condition as string) ?? "");
    }
  }, [selectedEdgeId, edge]);

  if (!selectedEdgeId || !edge) return null;

  const sourceNode = nodes.find((n) => n.id === edge.source);
  const targetNode = nodes.find((n) => n.id === edge.target);

  const handleTypeChange = (newType: EdgeType) => {
    setEdgeType(newType);
    updateEdgeData(selectedEdgeId, newType, newType === "conditional" ? condition : undefined);
  };

  const handleConditionChange = (value: string) => {
    setCondition(value);
    updateEdgeData(selectedEdgeId, edgeType, value);
  };

  return (
    <aside className="w-72 flex-shrink-0 bg-white border-l border-slate-200 p-4 flex flex-col gap-4 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center gap-2">
        <ArrowRight size={16} className="text-indigo-600" />
        <h2 className="font-semibold text-slate-800 text-sm flex-1">
          Kanten-Einstellungen
        </h2>
        <button
          onClick={() => selectEdge(null)}
          className="text-slate-400 hover:text-slate-600"
        >
          <X size={16} />
        </button>
      </div>

      {/* Connection info */}
      <div className="rounded-lg bg-slate-50 p-3 text-xs text-slate-600 space-y-1">
        <p>
          <strong>Von:</strong>{" "}
          {sourceNode ? (sourceNode.data as { label: string }).label : edge.source}
        </p>
        <p>
          <strong>Nach:</strong>{" "}
          {targetNode ? (targetNode.data as { label: string }).label : edge.target}
        </p>
      </div>

      {/* Edge type */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-slate-500">Typ</label>
        <div className="flex gap-2">
          <button
            onClick={() => handleTypeChange("linear")}
            className={[
              "flex-1 text-sm px-3 py-2 rounded-lg border transition-colors",
              edgeType === "linear"
                ? "bg-slate-100 border-slate-400 text-slate-800 font-medium"
                : "bg-white border-slate-200 text-slate-500 hover:border-slate-300",
            ].join(" ")}
          >
            Linear
          </button>
          <button
            onClick={() => handleTypeChange("conditional")}
            className={[
              "flex-1 text-sm px-3 py-2 rounded-lg border transition-colors",
              edgeType === "conditional"
                ? "bg-indigo-50 border-indigo-400 text-indigo-800 font-medium"
                : "bg-white border-slate-200 text-slate-500 hover:border-slate-300",
            ].join(" ")}
          >
            Bedingt
          </button>
        </div>
      </div>

      {/* Condition value (only for conditional edges) */}
      {edgeType === "conditional" && (
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">
            Bedingung (Routing-Wert)
          </label>
          <input
            type="text"
            value={condition}
            onChange={(e) => handleConditionChange(e.target.value)}
            placeholder='z.B. "rework" oder "approve"'
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
          />
          <p className="text-xs text-slate-400 mt-1">
            Dieser Wert wird mit <code className="bg-slate-100 px-1 rounded">route_decision</code> im
            State verglichen, um den Pfad zu bestimmen.
          </p>
        </div>
      )}

      {/* Preset conditions */}
      {edgeType === "conditional" && (
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-500">
            Schnellauswahl
          </label>
          <div className="flex gap-2 flex-wrap">
            {["approve", "rework", "done", "escalate"].map((preset) => (
              <button
                key={preset}
                onClick={() => handleConditionChange(preset)}
                className={[
                  "text-xs px-2 py-1 rounded-full border transition-colors",
                  condition === preset
                    ? "bg-indigo-600 text-white border-indigo-600"
                    : "bg-white text-slate-600 border-slate-200 hover:border-indigo-300",
                ].join(" ")}
              >
                {preset}
              </button>
            ))}
          </div>
        </div>
      )}
    </aside>
  );
}
