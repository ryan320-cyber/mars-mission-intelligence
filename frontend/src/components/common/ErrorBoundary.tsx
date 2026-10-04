import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props {
  children: ReactNode;
  fallbackTitle?: string;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught telemetry/component error:", error, errorInfo);
  }

  public handleReset = () => {
    this.setState({ hasError: false, error: undefined });
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="bg-mars-panel border border-rose-500/30 rounded-lg p-6 my-4 text-slate-200">
          <div className="flex items-center gap-3 text-rose-400 mb-2">
            <AlertTriangle className="w-5 h-5 flex-shrink-0" />
            <h3 className="font-bold text-sm">
              {this.props.fallbackTitle || "Scientific Module Display Error"}
            </h3>
          </div>
          <p className="text-xs text-slate-400 mb-4 font-mono">
            {this.state.error?.message || "An unexpected error occurred while parsing telemetry visualizer."}
          </p>
          <button
            onClick={this.handleReset}
            className="flex items-center gap-2 px-3 py-1.5 rounded bg-mars-surface hover:bg-mars-surface/80 border border-mars-border text-xs font-mono text-mars-cyan transition"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Retry Module
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
