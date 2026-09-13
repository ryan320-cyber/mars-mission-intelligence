import React from "react";
import { BookOpen, CheckCircle, Code, Shield, AlertTriangle, Layers, Cpu } from "lucide-react";

export const ScienceNotebook: React.FC = () => {
  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      {/* Module Banner */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-6 space-y-2">
        <div className="text-xs font-mono text-mars-cyan">MODULE 10</div>
        <h2 className="text-2xl font-bold text-white flex items-center gap-2 font-sans">
          <BookOpen className="w-6 h-6 text-mars-amber" />
          SCIENCE NOTEBOOK & METHODOLOGY WALKTHROUGH
        </h2>
        <p className="text-xs text-slate-300 font-mono">
          Transparent, reproducible scientific documentation of data engineering, mathematical formulas, ML evaluation, and index derivation.
        </p>
      </div>

      {/* Reproducibility Specification Card (Directive 43) */}
      <div className="bg-mars-panel border border-mars-border rounded-xl p-6 font-mono text-xs space-y-4 shadow-panel">
        <div className="flex items-center justify-between border-b border-mars-border pb-2">
          <h3 className="font-bold text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-emerald-400" />
            REPRODUCIBILITY & SYSTEM RELEASES
          </h3>
          <span className="text-emerald-400 font-bold">SHA-256 AUDITED</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="p-3 bg-mars-surface rounded border border-mars-border">
            <span className="text-slate-500 text-[10px] block">DATA PIPELINE</span>
            <span className="text-white font-bold">v1.0.0 (FastAPI Core)</span>
          </div>
          <div className="p-3 bg-mars-surface rounded border border-mars-border">
            <span className="text-slate-500 text-[10px] block">MECI INDEX FORMULA</span>
            <span className="text-mars-amber font-bold">MECI-2026-R1</span>
          </div>
          <div className="p-3 bg-mars-surface rounded border border-mars-border">
            <span className="text-slate-500 text-[10px] block">ML ARCHITECTURE</span>
            <span className="text-mars-cyan font-bold">RF-Ridge-TS-v1</span>
          </div>
          <div className="p-3 bg-mars-surface rounded border border-mars-border">
            <span className="text-slate-500 text-[10px] block">PDS ARCHIVE SYNC</span>
            <span className="text-slate-300">August 2026 Telemetry</span>
          </div>
        </div>
      </div>

      {/* Workflow Section 1: Ingestion & Quality Checks */}
      <div className="bg-mars-panel border border-mars-border rounded-xl p-6 space-y-4 shadow-panel">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-mars-amber text-mars-darkest font-mono font-bold text-xs flex items-center justify-center">
            01
          </span>
          <h3 className="text-base font-bold text-white font-sans">
            Data Quality & Automated Validation Layer (Directive 17)
          </h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          Every raw telemetry record from the NASA Mars Weather Service and PDS4 archives passes through an automated validation filter before analytical processing:
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs font-mono">
          <div className="p-3 bg-mars-surface rounded border border-mars-border space-y-1">
            <span className="text-mars-cyan font-bold block">Physical Range Verification:</span>
            <p className="text-slate-400 font-sans text-[11px]">
              Surface temperatures must satisfy <code className="text-slate-200">-130°C ≤ T ≤ +35°C</code> and atmospheric pressure must satisfy <code className="text-slate-200">500 Pa ≤ P ≤ 1250 Pa</code>. Values outside physical bounds are quarantined as sensor dropouts.
            </p>
          </div>
          <div className="p-3 bg-mars-surface rounded border border-mars-border space-y-1">
            <span className="text-mars-cyan font-bold block">Temporal Continuity & Sensor Gaps:</span>
            <p className="text-slate-400 font-sans text-[11px]">
              Observational gaps <code className="text-slate-200">ΔSol &gt; 1</code> are tagged and surfaced in charts rather than silently interpolated, preserving empirical integrity.
            </p>
          </div>
        </div>
      </div>

      {/* Workflow Section 2: Solar Longitude & Season Mapping */}
      <div className="bg-mars-panel border border-mars-border rounded-xl p-6 space-y-4 shadow-panel">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-mars-amber text-mars-darkest font-mono font-bold text-xs flex items-center justify-center">
            02
          </span>
          <h3 className="text-base font-bold text-white font-sans">
            Planetary Orbital Seasons & Solar Longitude Ls (Directive 14)
          </h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          Because Mars has an eccentric orbit (<code className="text-mars-cyan font-mono">e = 0.0934</code>), terrestrial Earth months do not represent Martian seasonal cycles. We calculate planetary season directly from Solar Longitude (<code className="text-mars-amber font-mono">Ls</code>):
        </p>
        <div className="p-4 bg-mars-surface rounded border border-mars-border font-mono text-xs space-y-2">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
            <div className="p-2 bg-mars-panel rounded border border-mars-border">
              <strong className="text-emerald-400 block">Ls 0° — 90°</strong>
              <span className="text-slate-400">Northern Spring / Southern Autumn</span>
            </div>
            <div className="p-2 bg-mars-panel rounded border border-mars-border">
              <strong className="text-sky-400 block">Ls 90° — 180°</strong>
              <span className="text-slate-400">Northern Summer / Aphelion (Coldest)</span>
            </div>
            <div className="p-2 bg-mars-panel rounded border border-mars-border">
              <strong className="text-mars-amber block">Ls 180° — 270°</strong>
              <span className="text-slate-400">Northern Autumn / Dust Storm Season</span>
            </div>
            <div className="p-2 bg-mars-panel rounded border border-mars-border">
              <strong className="text-rose-400 block">Ls 270° — 360°</strong>
              <span className="text-slate-400">Northern Winter / Perihelion (Max Insolation)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Workflow Section 3: Dual-Mode Anomaly Intelligence */}
      <div className="bg-mars-panel border border-mars-border rounded-xl p-6 space-y-4 shadow-panel">
        <div className="flex items-center gap-2">
          <span className="w-6 h-6 rounded-full bg-mars-amber text-mars-darkest font-mono font-bold text-xs flex items-center justify-center">
            03
          </span>
          <h3 className="text-base font-bold text-white font-sans">
            Dual-Mode Anomaly Intelligence (Directive 18 & 19)
          </h3>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed font-sans">
          Martian weather distributions exhibit non-Gaussian, heavy-tailed extremes. To eliminate bias from standard Z-scores, we implement a dual-mode statistical architecture:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 font-mono text-xs">
          <div className="p-4 bg-mars-surface rounded border border-mars-border space-y-2">
            <span className="font-bold text-mars-cyan">Univariate: Robust Median Absolute Deviation (MAD)</span>
            <code className="block text-[11px] text-slate-300 bg-mars-panel p-2 rounded">
              Z_mod = 0.6745 * (x - median(X)) / MAD
            </code>
            <p className="text-[11px] text-slate-400 font-sans">
              Robust against extreme dust storms that would otherwise distort the sample mean and standard deviation.
            </p>
          </div>
          <div className="p-4 bg-mars-surface rounded border border-mars-border space-y-2">
            <span className="font-bold text-mars-amber">Multivariate: Scikit-Learn Isolation Forest</span>
            <code className="block text-[11px] text-slate-300 bg-mars-panel p-2 rounded">
              X = [T_max, T_min, ΔT, Pressure]
            </code>
            <p className="text-[11px] text-slate-400 font-sans">
              Isolates rare joint physical states where no individual variable is an extreme outlier, but their multidimensional combination represents an abnormal atmospheric disturbance.
            </p>
          </div>
        </div>
      </div>

      {/* Scientific Disclaimers (Directive 78) */}
      <div className="bg-mars-panel border border-mars-border rounded-xl p-6 space-y-3 font-mono text-xs">
        <div className="flex items-center gap-2 text-mars-amber font-bold">
          <Shield className="w-4 h-4" />
          <span>SCIENTIFIC INTEGRITY & REGULATORY LABELS (DIRECTIVE 78)</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-[11px]">
          <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
            <strong className="text-white block font-mono">OBSERVED DATA:</strong>
            <span className="text-slate-400">Authentic measurements retrieved from calibrated NASA PDS instruments.</span>
          </div>
          <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
            <strong className="text-mars-cyan block font-mono">MODEL OUTPUT:</strong>
            <span className="text-slate-400">Predictive values generated by ML pipelines trained strictly on past observations.</span>
          </div>
          <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
            <strong className="text-mars-amber block font-mono">PROJECT ANALYTICAL INDEX:</strong>
            <span className="text-slate-400">The MECI score is an engineering volatility index created for this challenge.</span>
          </div>
          <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
            <strong className="text-rose-400 block font-mono">SIMULATED SCENARIO:</strong>
            <span className="text-slate-400">Hypothetical sensitivity calculations clearly marked as non-forecast experiments.</span>
          </div>
        </div>
      </div>
    </div>
  );
};
