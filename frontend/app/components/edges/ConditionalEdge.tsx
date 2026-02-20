"use client";

import { memo } from "react";
import {
  EdgeProps,
  BaseEdge,
  EdgeLabelRenderer,
  getSmoothStepPath,
} from "@xyflow/react";

export const ConditionalEdge = memo(function ConditionalEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  markerEnd,
}: EdgeProps) {
  const [edgePath, labelX, labelY] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const condition = data?.condition as string | undefined;

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        markerEnd={markerEnd}
        style={{
          strokeDasharray: "6 3",
          stroke: "#6366f1",
          strokeWidth: 2,
        }}
      />
      {condition && (
        <EdgeLabelRenderer>
          <div
            style={{
              position: "absolute",
              transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
              pointerEvents: "all",
            }}
            className="bg-indigo-600 text-white text-xs px-2 py-0.5 rounded-full font-medium shadow nodrag nopan"
          >
            {condition}
          </div>
        </EdgeLabelRenderer>
      )}
    </>
  );
});
