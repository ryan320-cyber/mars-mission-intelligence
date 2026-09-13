import React, { useState } from "react";
import { 
  Bot, 
  Send, 
  Sparkles, 
  ExternalLink, 
  ShieldCheck, 
  HelpCircle, 
  AlertCircle,
  Database,
  ArrowRight
} from "lucide-react";
import { AIResponse } from "../../lib/types";
import { api } from "../../lib/api";

interface MarsAIScientistProps {
  onNavigate: (tabId: string, sol?: number) => void;
}

const PRESETS = [
  "Explain the major detected anomalies",
  "Why does the Environmental Challenge Index peak in certain seasons?",
  "Compare atmospheric pressure in Gale Crater vs Elysium Planitia",
  "Where does the diurnal temperature forecasting model fail?",
  "How does vertical atmospheric structure change during dust storms?",
  "What are the limitations of Curiosity wind data?"
];

export const MarsAIScientist: React.FC<MarsAIScientistProps> = ({ onNavigate }) => {
  const [queryText, setQueryText] = useState<string>("");
  const [response, setResponse] = useState<AIResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleQuery = (text: string) => {
    if (!text.trim()) return;
    setLoading(true);
    setQueryText(text);
    api.queryAI(text)
      .then((res) => {
        setResponse(res);
        setLoading(false);
      })
      .catch((err) => {
        console.error("AI query error:", err);
        setLoading(false);
      });
  };

  return (
    <div className="space-y-6">
      {/* Module Banner */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 08</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Bot className="w-5 h-5 text-mars-cyan" />
            MARS GROUNDED AI SCIENTIST
          </h2>
          <p className="text-xs text-slate-400">
            Scientifically grounded assistant adhering to the NASA Data Evidence Contract. Refuses false certainty and provides verifiable evidence traces.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
          <span className="px-2.5 py-1 rounded bg-mars-surface border border-mars-border text-mars-cyan flex items-center gap-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Anti-Hallucination Guardrails Active</span>
          </span>
        </div>
      </div>

      {/* Preset Inquiries (Directive 39) */}
      <div className="space-y-2">
        <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-mars-amber" />
          <span>PRESET SCIENTIFIC INQUIRIES:</span>
        </span>
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleQuery(p)}
              className="px-3 py-1.5 rounded bg-mars-surface hover:bg-mars-border border border-mars-border text-xs font-mono text-slate-300 hover:text-white transition-all text-left"
            >
              {p}
            </button>
          ))}
        </div>
      </div>

      {/* Query Input Bar */}
      <div className="flex gap-2">
        <input
          type="text"
          value={queryText}
          onChange={(e) => setQueryText(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleQuery(queryText)}
          placeholder="Ask a scientific question about Mars atmospheric data, anomalies, or models..."
          className="flex-1 px-4 py-3 bg-mars-panel border border-mars-border rounded-lg text-xs font-mono text-white placeholder-slate-500 focus:outline-none focus:border-mars-cyan"
        />
        <button
          onClick={() => handleQuery(queryText)}
          disabled={loading || !queryText.trim()}
          className="px-5 py-3 rounded-lg bg-mars-cyan hover:bg-sky-400 text-mars-darkest font-mono font-bold text-xs transition-all disabled:opacity-40 flex items-center gap-2"
        >
          <Send className="w-4 h-4" />
          <span>{loading ? "ANALYZING..." : "QUERY"}</span>
        </button>
      </div>

      {/* Structured AI Answer Contract Card (Directive 38 & 61: WOW Moment 2) */}
      {response && (
        <div className="bg-mars-panel border border-mars-border rounded-xl p-6 space-y-5 shadow-panel">
          {/* Header & Data Sufficiency Badge (Directive 62) */}
          <div className="flex items-center justify-between border-b border-mars-border pb-3">
            <div className="flex items-center gap-2 font-mono text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-white font-bold">SCIENTIFIC ANSWER CONTRACT</span>
            </div>

            <div className="flex items-center gap-2 font-mono text-xs">
              <span className="text-slate-500">DATA SUFFICIENCY:</span>
              <span className={`px-2 py-0.5 rounded font-bold ${
                response.data_sufficiency === "HIGH"
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                  : response.data_sufficiency === "INSUFFICIENT"
                  ? "bg-rose-500/20 text-rose-400 border border-rose-500/40"
                  : "bg-amber-500/20 text-amber-400 border border-amber-500/40"
              }`}>
                {response.data_sufficiency}
              </span>
            </div>
          </div>

          {/* 1. FINDING */}
          <div className="space-y-1">
            <span className="text-[10px] font-mono font-bold text-mars-amber uppercase tracking-wider block">
              01 — EMPIRICAL FINDING
            </span>
            <p className="text-sm font-semibold text-white leading-relaxed">
              {response.finding}
            </p>
          </div>

          {/* 2. DATA EVIDENCE */}
          <div className="p-3.5 bg-mars-surface rounded-lg border border-mars-border space-y-1 font-mono text-xs">
            <span className="text-[10px] text-mars-cyan font-bold block uppercase tracking-wider">
              02 — AUTHORITATIVE DATA EVIDENCE
            </span>
            <p className="text-slate-200 leading-relaxed font-sans text-xs">
              {response.data_evidence}
            </p>
          </div>

          {/* 3. ANALYTICAL INTERPRETATION */}
          <div className="space-y-1">
            <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider block">
              03 — PLANETARY SCIENTIFIC INTERPRETATION
            </span>
            <p className="text-xs text-slate-300 leading-relaxed font-sans">
              {response.analytical_interpretation}
            </p>
          </div>

          {/* 4. LIMITATIONS & FALSE CERTAINTY CHECK (Directive 40) */}
          <div className="p-3 bg-mars-surface/50 rounded-lg border border-mars-border text-xs space-y-1">
            <span className="text-[10px] font-mono text-rose-400 font-bold block uppercase tracking-wider flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              <span>04 — SCIENTIFIC UNCERTAINTY & SENSOR LIMITATIONS</span>
            </span>
            <p className="text-slate-400 font-sans text-[11px] leading-relaxed">
              {response.limitations}
            </p>
          </div>

          {/* 5. SOURCE PROVENANCE */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-2 border-t border-mars-border text-xs font-mono text-slate-400">
            <div className="flex items-center gap-2">
              <Database className="w-3.5 h-3.5 text-mars-cyan" />
              <span>Source: <strong className="text-slate-200">{response.source}</strong></span>
            </div>

            {/* Signature WOW Moment 2: Clickable Evidence Trace Links */}
            {response.evidence_links && response.evidence_links.length > 0 && (
              <div className="flex flex-wrap items-center gap-2">
                {response.evidence_links.map((link, idx) => (
                  <button
                    key={idx}
                    onClick={() => onNavigate(link.target, link.sol)}
                    className="px-2.5 py-1 rounded bg-mars-surface hover:bg-mars-border border border-mars-cyan/40 text-mars-cyan font-bold transition-all flex items-center gap-1"
                  >
                    <span>{link.label}</span>
                    <ArrowRight className="w-3 h-3" />
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};
