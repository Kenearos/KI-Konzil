"use client";

import { ReactFlowProvider } from "@xyflow/react";
import { Save, Download } from "lucide-react";
import { ArchitectCanvas } from "@/app/components/ArchitectCanvas";
import { NodeSidebar } from "@/app/components/panels/NodeSidebar";
import { NodeSettingsPanel } from "@/app/components/panels/NodeSettingsPanel";
import { EdgeSettingsPanel } from "@/app/components/panels/EdgeSettingsPanel";
import { useCouncilStore } from "@/app/store/council-store";
import { parseGraphToBlueprint } from "@/app/utils/blueprint-parser";
import { councilApi } from "@/app/utils/api-client";

export default function RatArchitektPage() {
  const nodes = useCouncilStore((s) => s.nodes);
  const edges = useCouncilStore((s) => s.edges);
  const councilName = useCouncilStore((s) => s.councilName);
  const setCouncilName = useCouncilStore((s) => s.setCouncilName);
  const selectedNodeId = useCouncilStore((s) => s.selectedNodeId);
  const selectedEdgeId = useCouncilStore((s) => s.selectedEdgeId);

  const handleSave = async () => {
    const blueprint = parseGraphToBlueprint(nodes, edges, councilName);
    try {
      await councilApi.create(blueprint);
      alert("Rat gespeichert!");
    } catch (e) {
      alert("Fehler beim Speichern: " + (e as Error).message);
    }
  };

  const handleExport = () => {
    const blueprint = parseGraphToBlueprint(nodes, edges, councilName);
    const blob = new Blob([JSON.stringify(blueprint, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${councilName.replace(/\s+/g, "-")}-blueprint.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Toolbar */}
      <header className="flex items-center gap-3 px-4 py-2 border-b border-slate-200 bg-white flex-shrink-0">
        <input
          type="text"
          value={councilName}
          onChange={(e) => setCouncilName(e.target.value)}
          className="font-semibold text-slate-800 bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-indigo-300 rounded px-1"
        />
        <span className="text-slate-300">|</span>
        <span className="text-xs text-slate-400">{nodes.length} Agenten · {edges.length} Kanten</span>
        <div className="ml-auto flex gap-2">
          <button
            onClick={handleExport}
            className="flex items-center gap-1.5 text-sm text-slate-600 border border-slate-200 px-3 py-1.5 rounded-lg hover:bg-slate-50 transition-colors"
          >
            <Download size={14} />
            Export
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-1.5 text-sm text-white bg-indigo-600 px-3 py-1.5 rounded-lg hover:bg-indigo-700 transition-colors"
          >
            <Save size={14} />
            Speichern
          </button>
        </div>
      </header>

      {/* Main area */}
      <div className="flex flex-1 overflow-hidden">
        <ReactFlowProvider>
          <NodeSidebar />
          <ArchitectCanvas />
          {selectedNodeId && <NodeSettingsPanel />}
          {selectedEdgeId && <EdgeSettingsPanel />}
        </ReactFlowProvider>
      </div>
    </div>
  );
}
