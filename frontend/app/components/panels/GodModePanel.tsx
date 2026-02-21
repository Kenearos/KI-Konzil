"use client";

import { useState } from "react";
import { Check, X, Pencil, Shield } from "lucide-react";
import { GodModeAction } from "@/app/types/council";
import { PauseInfo } from "@/app/hooks/useCouncilWebSocket";

interface Props {
  pauseInfo: PauseInfo;
  onAction: (action: GodModeAction, modifiedDraft?: string) => void;
  isResuming: boolean;
}

// God Mode approval panel — shown when the graph pauses at a node
export function GodModePanel({ pauseInfo, onAction, isResuming }: Props) {
  const [editMode, setEditMode] = useState(false);
  const [editedDraft, setEditedDraft] = useState(pauseInfo.current_draft);

  const handleModify = () => {
    if (editMode) {
      onAction("modify", editedDraft);
      setEditMode(false);
    } else {
      setEditedDraft(pauseInfo.current_draft);
      setEditMode(true);
    }
  };

  return (
    <div className="rounded-xl border-2 border-amber-300 bg-amber-50 p-4 space-y-3">
      {/* Header */}
      <div className="flex items-center gap-2">
        <Shield size={18} className="text-amber-600" />
        <h3 className="font-semibold text-sm text-amber-800">
          God Mode — Freigabe erforderlich
        </h3>
      </div>

      {/* Info about which node is next */}
      <div className="text-xs text-amber-700 space-y-1">
        <p>
          <strong>Nächster Agent:</strong>{" "}
          {pauseInfo.next_nodes.join(", ") || "—"}
        </p>
        {pauseInfo.iteration_count != null && (
          <p>
            <strong>Iteration:</strong> {pauseInfo.iteration_count}
          </p>
        )}
        {pauseInfo.critic_score != null && (
          <p>
            <strong>Bewertung:</strong> {pauseInfo.critic_score}/10
          </p>
        )}
      </div>

      {/* Current draft preview / editor */}
      <div className="flex flex-col gap-1">
        <label className="text-xs font-medium text-amber-700">
          Aktueller Entwurf
        </label>
        {editMode ? (
          <textarea
            value={editedDraft}
            onChange={(e) => setEditedDraft(e.target.value)}
            rows={8}
            className="rounded-lg border border-amber-300 bg-white px-3 py-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-amber-400"
          />
        ) : (
          <div className="rounded-lg bg-white border border-amber-200 p-3 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed max-h-48 overflow-y-auto">
            {pauseInfo.current_draft || (
              <span className="italic text-slate-400">Kein Entwurf vorhanden</span>
            )}
          </div>
        )}
      </div>

      {/* Action buttons */}
      <div className="flex gap-2">
        <button
          onClick={() => onAction("approve")}
          disabled={isResuming}
          className="flex items-center gap-1.5 text-sm text-white bg-green-600 px-3 py-1.5 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
        >
          <Check size={14} />
          Genehmigen
        </button>
        <button
          onClick={handleModify}
          disabled={isResuming}
          className="flex items-center gap-1.5 text-sm text-white bg-blue-600 px-3 py-1.5 rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <Pencil size={14} />
          {editMode ? "Änderung senden" : "Ändern"}
        </button>
        <button
          onClick={() => onAction("reject")}
          disabled={isResuming}
          className="flex items-center gap-1.5 text-sm text-white bg-red-500 px-3 py-1.5 rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50"
        >
          <X size={14} />
          Ablehnen
        </button>
      </div>

      {isResuming && (
        <p className="text-xs text-amber-600 animate-pulse">
          Wird fortgesetzt…
        </p>
      )}
    </div>
  );
}
