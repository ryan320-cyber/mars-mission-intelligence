import React, { Component, ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo);
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="border border-amber-500/30 bg-amber-950/20 backdrop-blur-md rounded-xl p-6 text-slate-300">
          <div className="flex items-center gap-3 mb-3">
            <span className="flex h-3 w-3 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-amber-500"></span>
            </span>
            <h3 className="text-sm font-semibold tracking-wider font-mono uppercase text-amber-400">
              {this.props.fallbackTitle || "TELEMETRY STREAM INTERRUPTED"}
            </h3>
          </div>
          <p className="text-xs text-slate-400 mb-4 leading-relaxed">
            The module encountered a temporary telemetry fetch or rendering fault while communicating with the data server.
            {this.state.error && (
              <span className="block mt-2 font-mono text-[11px] text-amber-300/80 bg-slate-900/60 p-2 rounded border border-slate-800">
                {this.state.error.message}
              </span>
            )}
          </p>
          <div className="flex items-center gap-3">
            <button
              onClick={this.handleRetry}
              className="px-4 py-1.5 text-xs font-mono font-medium rounded-lg bg-amber-500/20 hover:bg-amber-500/30 text-amber-300 border border-amber-500/40 transition-colors"
            >
              Retry Telemetry Stream
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-3 py-1.5 text-xs font-mono rounded-lg bg-slate-800/60 hover:bg-slate-800 text-slate-400 transition-colors"
            >
              Reload Interface
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
