import React, { useState, useEffect } from "react";
import { BrainCircuit, BarChart, AlertCircle, CheckCircle, TrendingUp, Info } from "lucide-react";
import { ModelLabData } from "../../lib/types";
import { api } from "../../lib/api";

export const ModelLab: React.FC = () => {
  const [modelData, setModelData] = useState<ModelLabData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    api.getModelLab()
      .then((res) => {
        if (isMounted) {
          setModelData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load Model Lab:", err);
        setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  if (loading || !modelData) {
    return (
      <div className="p-8 text-center font-mono text-xs text-slate-400">
        Loading Machine Learning Model Lab & Evaluation Metrics...
      </div>
    );
  }

  const split = modelData.dataset_split;
  const models = modelData.models_comparison;
  const features = modelData.feature_importances;
  const slices = modelData.slice_error_analysis.seasonal_slices;

  return (
    <div className="space-y-6">
      {/* Module Banner */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 07</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-mars-amber" />
            MACHINE LEARNING MODEL LAB & EXPLAINABILITY
          </h2>
          <p className="text-xs text-slate-400">
            Task: {modelData.task_description}. Baseline-first evaluation with strict chronological time-aware validation.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
          <span className="px-2 py-1 rounded bg-mars-surface border border-mars-border text-emerald-400">
            Zero Future Lookahead
          </span>
        </div>
      </div>

      {/* Dataset Chronological Split Details (Directive 25) */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
        <div className="bg-mars-panel border border-mars-border rounded-lg p-4 space-y-1">
          <span className="text-slate-500 text-[10px]">1. TRAINING SET (CHRONOLOGICAL 70%)</span>
          <div className="text-base font-bold text-white">{split.train_samples} Continuous Sols</div>
          <div className="text-[11px] text-slate-400">{split.train_sol_range}</div>
        </div>

        <div className="bg-mars-panel border border-mars-border rounded-lg p-4 space-y-1">
          <span className="text-slate-500 text-[10px]">2. VALIDATION SET (15%)</span>
          <div className="text-base font-bold text-sky-400">{split.val_samples} Sols</div>
          <div className="text-[11px] text-slate-400">Hyperparameter Regularization Tuning</div>
        </div>

        <div className="bg-mars-panel border border-mars-border rounded-lg p-4 space-y-1">
          <span className="text-slate-500 text-[10px]">3. OUT-OF-SAMPLE TEST SET (15%)</span>
          <div className="text-base font-bold text-mars-amber">{split.test_samples} Sols</div>
          <div className="text-[11px] text-slate-400">{split.test_sol_range}</div>
        </div>
      </div>

      {/* Baseline vs ML Comparison Table (Directive 24) */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-5 space-y-4 font-mono text-xs shadow-panel">
        <div className="flex items-center justify-between border-b border-mars-border pb-3">
          <h3 className="font-bold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-mars-cyan" />
            BASELINE-FIRST PERFORMANCE COMPARISON (TEST SET)
          </h3>
          <span className="text-[10px] text-slate-400">Metrics: MAE, RMSE (°C), R² Score</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-mars-surface text-slate-400 text-[10px] uppercase border-b border-mars-border">
              <tr>
                <th className="py-2.5 px-3">Model Architecture</th>
                <th className="py-2.5 px-3">Type</th>
                <th className="py-2.5 px-3">MAE (°C)</th>
                <th className="py-2.5 px-3">RMSE (°C)</th>
                <th className="py-2.5 px-3">R² Score</th>
                <th className="py-2.5 px-3 text-right">Baseline Delta</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-mars-border/40 text-slate-300">
              {models.map((m, idx) => (
                <tr key={idx} className={m.type === "Machine Learning" ? "bg-mars-surface/40" : ""}>
                  <td className="py-3 px-3 font-bold text-white flex items-center gap-2">
                    {m.model_name.includes("Selected") && (
                      <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
                    )}
                    <span>{m.model_name}</span>
                  </td>
                  <td className="py-3 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] ${
                      m.type === "Baseline" ? "bg-slate-800 text-slate-400" : "bg-mars-surface text-mars-cyan border border-mars-cyan/30"
                    }`}>
                      {m.type}
                    </span>
                  </td>
                  <td className="py-3 px-3 font-bold text-slate-200">{m.mae} °C</td>
                  <td className="py-3 px-3">{m.rmse} °C</td>
                  <td className="py-3 px-3 text-mars-amber">{m.r2}</td>
                  <td className="py-3 px-3 text-right font-bold text-emerald-400">
                    {m.improvement_over_baseline_pct ? `+${m.improvement_over_baseline_pct}% MAE Gain` : "Reference"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Feature Importance & Explainability (Directive 27) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Feature Importance Bars */}
        <div className="bg-mars-panel border border-mars-border rounded-lg p-5 space-y-4 font-mono text-xs shadow-panel">
          <div className="flex items-center justify-between border-b border-mars-border pb-2">
            <h3 className="font-bold text-white">WHAT MATTERED? (FEATURE IMPORTANCE)</h3>
            <span className="text-[10px] text-slate-400">Random Forest Impurity Decrease</span>
          </div>

          <div className="space-y-3">
            {features.map((f, i) => (
              <div key={i} className="space-y-1">
                <div className="flex justify-between text-slate-300">
                  <span>{f.feature}</span>
                  <span className="text-mars-cyan font-bold">{f.importance}%</span>
                </div>
                <div className="w-full h-2 bg-mars-surface rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-mars-cyan to-mars-amber rounded-full"
                    style={{ width: `${f.importance}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <p className="text-[11px] text-slate-400 font-sans leading-relaxed pt-2">
            Prior Sol diurnal thermal swing and pressure derivatives constitute &gt;70% of predictive power, confirming that boundary layer heat retention on Mars exhibits high day-to-day inertia except during dust storm events.
          </p>
        </div>

        {/* Slice-Based Error Analysis & Honest Failure Case (Directive 76) */}
        <div className="bg-mars-panel border border-mars-border rounded-lg p-5 space-y-4 font-mono text-xs shadow-panel">
          <div className="flex items-center justify-between border-b border-mars-border pb-2">
            <h3 className="font-bold text-white flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-rose-400" />
              <span>HONEST FAILURE CASE & SEASONAL SLICE ANALYSIS</span>
            </h3>
            <span className="text-[10px] text-rose-400 font-bold">Directive 76</span>
          </div>

          <div className="space-y-2">
            {Object.entries(slices).map(([season, stats]) => (
              <div key={season} className="p-2.5 bg-mars-surface rounded border border-mars-border flex justify-between items-center">
                <div>
                  <div className="font-bold text-slate-200">{season}</div>
                  <div className="text-[10px] text-slate-400">{stats.sample_count} Test Sols</div>
                </div>
                <div className="text-right">
                  <div className="text-rose-400 font-bold">MAE: {stats.mae} °C</div>
                  <div className="text-[10px] text-slate-500">Max Error: {stats.max_error} °C</div>
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 bg-mars-surface/60 rounded border border-mars-border text-[11px] text-slate-300 font-sans leading-relaxed">
            <span className="font-mono text-mars-amber font-bold block mb-1">SCIENTIFIC LIMITATION REPORT:</span>
            {modelData.slice_error_analysis.failure_case_analysis}
          </div>
        </div>
      </div>
    </div>
  );
};
