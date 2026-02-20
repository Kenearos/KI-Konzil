"use client";

import { useCallback } from "react";
import { Bot, Plus } from "lucide-react";
import { useCouncilStore } from "@/app/store/council-store";

// Sidebar panel — drag or click to add agent nodes to the canvas
export function NodeSidebar() {
  const addAgentNode = useCouncilStore((s) => s.addAgentNode);

  const onDragStart = useCallback(
    (event: React.DragEvent<HTMLDivElement>) => {
      event.dataTransfer.setData("application/reactflow", "agentNode");
      event.dataTransfer.effectAllowed = "move";
    },
    []
  );

  const handleAddClick = useCallback(() => {
    // Add node at a reasonable default position near the center
    addAgentNode({ x: 200 + Math.random() * 200, y: 100 + Math.random() * 200 });
  }, [addAgentNode]);

  return (
    <aside className="w-52 flex-shrink-0 bg-white border-r border-slate-200 p-4 flex flex-col gap-4">
      <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
        Komponenten
      </h2>

      {/* Draggable node template */}
      <div
        draggable
        onDragStart={onDragStart}
        onClick={handleAddClick}
        className="flex items-center gap-2 rounded-lg border-2 border-dashed border-indigo-300 bg-indigo-50 px-3 py-3 cursor-grab active:cursor-grabbing hover:border-indigo-500 hover:bg-indigo-100 transition-colors select-none"
        title="Auf Canvas ziehen oder klicken"
      >
        <Bot size={18} className="text-indigo-600" />
        <span className="text-sm font-medium text-indigo-700">Agent</span>
        <Plus size={14} className="text-indigo-400 ml-auto" />
      </div>

      <p className="text-xs text-slate-400 leading-snug">
        Ziehe einen Agent auf die Zeichenfläche oder klicke, um ihn hinzuzufügen.
      </p>

      <div className="mt-auto space-y-1">
        <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Kanten
        </p>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="block w-6 border-t-2 border-slate-400" />
          Linear
        </div>
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span className="block w-6 border-t-2 border-dashed border-indigo-500" />
          Bedingt
        </div>
      </div>
    </aside>
  );
}
