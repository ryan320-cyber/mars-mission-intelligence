import React from "react";

interface LoadingSkeletonProps {
  variant?: "card" | "kpi" | "chart" | "table";
  title?: string;
  className?: string;
}

export const LoadingSkeleton: React.FC<LoadingSkeletonProps> = ({
  variant = "card",
  title = "Acquiring NASA Telemetry Stream...",
  className = ""
}) => {
  if (variant === "kpi") {
    return (
      <div className={`border border-slate-800/80 bg-slate-900/50 backdrop-blur-md rounded-xl p-5 animate-pulse ${className}`}>
        <div className="flex justify-between items-center mb-3">
          <div className="h-3 w-24 bg-slate-800 rounded"></div>
          <div className="h-3 w-8 bg-cyan-950/60 rounded"></div>
        </div>
        <div className="h-8 w-36 bg-slate-800/80 rounded mb-2"></div>
        <div className="h-2.5 w-48 bg-slate-800/50 rounded"></div>
      </div>
    );
  }

  if (variant === "chart") {
    return (
      <div className={`border border-slate-800/80 bg-slate-900/50 backdrop-blur-md rounded-xl p-6 animate-pulse flex flex-col justify-between h-[360px] ${className}`}>
        <div className="flex justify-between items-center border-b border-slate-800/60 pb-3">
          <div className="space-y-2">
            <div className="h-4 w-48 bg-slate-800 rounded"></div>
            <div className="h-3 w-32 bg-slate-800/50 rounded"></div>
          </div>
          <div className="flex gap-2">
            <div className="h-6 w-16 bg-slate-800/60 rounded-md"></div>
            <div className="h-6 w-16 bg-slate-800/60 rounded-md"></div>
          </div>
        </div>
        <div className="flex-1 flex items-end gap-3 pt-6 pb-2 px-2">
          {[40, 65, 30, 85, 50, 70, 45, 90, 60, 75, 55, 80].map((h, i) => (
            <div
              key={i}
              className="flex-1 bg-slate-800/40 rounded-t border-t border-cyan-500/20"
              style={{ height: `${h}%` }}
            ></div>
          ))}
        </div>
        <div className="flex justify-between items-center pt-3 border-t border-slate-800/60 text-xs text-slate-500 font-mono">
          <span>{title}</span>
          <span className="flex items-center gap-1.5 text-cyan-400">
            <span className="inline-block w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
            WARMING CACHE
          </span>
        </div>
      </div>
    );
  }

  if (variant === "table") {
    return (
      <div className={`border border-slate-800/80 bg-slate-900/50 backdrop-blur-md rounded-xl p-5 animate-pulse ${className}`}>
        <div className="h-4 w-40 bg-slate-800 rounded mb-4"></div>
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="flex gap-4">
              <div className="h-4 w-1/4 bg-slate-800/60 rounded"></div>
              <div className="h-4 w-1/4 bg-slate-800/40 rounded"></div>
              <div className="h-4 w-1/4 bg-slate-800/60 rounded"></div>
              <div className="h-4 w-1/4 bg-slate-800/40 rounded"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Default card skeleton
  return (
    <div className={`border border-slate-800/80 bg-slate-900/50 backdrop-blur-md rounded-xl p-6 animate-pulse space-y-4 ${className}`}>
      <div className="flex justify-between items-center border-b border-slate-800/60 pb-3">
        <div className="h-5 w-48 bg-slate-800 rounded"></div>
        <div className="h-4 w-20 bg-slate-800/60 rounded"></div>
      </div>
      <div className="space-y-2.5">
        <div className="h-3.5 w-full bg-slate-800/40 rounded"></div>
        <div className="h-3.5 w-5/6 bg-slate-800/30 rounded"></div>
        <div className="h-3.5 w-2/3 bg-slate-800/40 rounded"></div>
      </div>
      <div className="pt-2 flex justify-between items-center text-xs text-slate-500 font-mono">
        <span>{title}</span>
        <span className="text-cyan-400/80">SYNCHRONIZING...</span>
      </div>
    </div>
  );
};
