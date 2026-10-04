import React from "react";

interface SkeletonProps {
  lines?: number;
  className?: string;
  type?: "card" | "chart" | "table" | "text";
}

export const SkeletonLoader: React.FC<SkeletonProps> = ({
  lines = 3,
  className = "",
  type = "card"
}) => {
  if (type === "chart") {
    return (
      <div className={`bg-mars-panel border border-mars-border rounded-lg p-6 animate-pulse ${className}`}>
        <div className="flex items-center justify-between mb-4">
          <div className="h-4 bg-mars-surface rounded w-1/3"></div>
          <div className="h-3 bg-mars-surface rounded w-1/6"></div>
        </div>
        <div className="h-64 bg-mars-surface/60 rounded flex items-end p-4 gap-2">
          {Array.from({ length: 16 }).map((_, i) => (
            <div
              key={i}
              className="bg-mars-surface rounded-t flex-1"
              style={{ height: `${20 + (i % 7) * 12}%` }}
            ></div>
          ))}
        </div>
      </div>
    );
  }

  if (type === "table") {
    return (
      <div className={`bg-mars-panel border border-mars-border rounded-lg p-5 animate-pulse space-y-3 ${className}`}>
        <div className="h-4 bg-mars-surface rounded w-1/4 mb-4"></div>
        {Array.from({ length: lines }).map((_, i) => (
          <div key={i} className="flex gap-4">
            <div className="h-3 bg-mars-surface rounded w-1/4"></div>
            <div className="h-3 bg-mars-surface rounded w-1/4"></div>
            <div className="h-3 bg-mars-surface rounded w-1/4"></div>
            <div className="h-3 bg-mars-surface rounded w-1/4"></div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`bg-mars-panel border border-mars-border rounded-lg p-5 animate-pulse space-y-3 ${className}`}>
      <div className="h-4 bg-mars-surface rounded w-2/5"></div>
      <div className="space-y-2 pt-2">
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className="h-3 bg-mars-surface/80 rounded"
            style={{ width: `${85 - (i * 15)}%` }}
          ></div>
        ))}
      </div>
    </div>
  );
};
