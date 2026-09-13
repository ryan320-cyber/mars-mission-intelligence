import React, { useState, useEffect } from "react";
import { ShieldAlert, Info, Sliders, Play, RotateCcw, AlertTriangle } from "lucide-react";
import { ChallengeIndexData } from "../../lib/types";
import { api } from "../../lib/api";

export const ChallengeIndexCard: React.FC = () => {
  const [indexData, setIndexData] = useState<ChallengeIndexData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Scenario Simulator State (Directive 32)
  const [tempMultiplier, setTempMultiplier] = useState<number>(1.0);
  const [pressureDrop, setPressureDrop] = useState<number>(0.0);
  const [dustStorm, setDustStorm] = useState<boolean>(false);
  const [simResult, setSimResult] = useState<any>(null);
  const [simulating, setSimulating] = useState<boolean>(false);

  useEffect(() => {
    let isMounted = true;
    api.getChallengeIndex()
      .then((res) => {
        if (isMounted) {
          setIndexData(res);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load Challenge Index:", err);
        setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  const runSimulation = () => {
    setSimulating(true);
    api.simulateScenario({
      temp_variability_multiplier: tempMultiplier,
      hypothetical_pressure_drop_pa: pressureDrop,
      dust_storm_active: dustStorm
    })
      .then((res) => {
        setSimResult(res);
        setSimulating(false);
      })
      .catch((err) => {
        console.error("Failed simulation:", err);
        setSimulating(false);
      });
  };

  const resetSimulation = () => {
    setTempMultiplier(1.0);
    setPressureDrop(0.0);
    setDustStorm(false);
    setSimResult(null);
  };

  if (loading || !indexData) {
    return (
      <div className="p-8 text-center font-mono text-xs text-slate-400">
        Computing Martian Environmental Challenge Index...
      </div>
    );
  }

  const factors = indexData.factor_breakdown;

  return (
    <div className="space-y-6">
      {/* Module Banner */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 06</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <ShieldAlert className="w-5 h-5 text-mars-rust" />
            MARTIAN ENVIRONMENTAL CHALLENGE INDEX (MECI)
          </h2>
          <p className="text-xs text-slate-400">
            A transparent engineering risk metric (0 — 100) tracking environmental volatility, thermal stress, and atmospheric dynamics.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
          <span>Project Index Formulation v1.0</span>
        </div>
      </div>

      {/* Main Score & Factor Decomposition Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Score Card */}
        <div className="bg-mars-panel border border-mars-border rounded-lg p-6 shadow-panel flex flex-col justify-between space-y-4">
          <div>
            <span className="text-xs font-mono text-slate-400">CURRENT COMPOSITE CHALLENGE SCORE</span>
            <div className="flex items-baseline gap-2 mt-2">
              <span className="text-6xl font-black font-mono text-mars-amber">
                {indexData.index_score}
              </span>
              <span className="text-sm font-mono text-slate-500">/ 100</span>
            </div>

            <div className="mt-2">
              <span
                className={`inline-block px-3 py-1 rounded text-xs font-mono font-bold tracking-wider ${
                  indexData.classification === "EXTREME"
                    ? "bg-rose-500/20 text-rose-400 border border-rose-500/40"
                    : indexData.classification === "HIGH"
                    ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                    : "bg-emerald-500/20 text-emerald-400 border border-emerald-500/40"
                }`}
              >
                {indexData.classification} CHALLENGE REGIME
              </span>
            </div>
          </div>

          {/* Mathematical Formula Box */}
          <div className="p-3 bg-mars-surface rounded border border-mars-border text-[11px] font-mono space-y-1">
            <span className="text-slate-400 block font-bold">TRANSPARENT DERIVATION:</span>
            <code className="text-mars-cyan block text-[10px]">
              {indexData.formula}
            </code>
          </div>

          <p className="text-[10px] text-slate-500 font-sans italic">
            {indexData.disclaimer}
          </p>
        </div>

        {/* Factor Breakdown Bars (Directive 30) */}
        <div className="lg:col-span-2 bg-mars-panel border border-mars-border rounded-lg p-6 space-y-5 font-mono text-xs shadow-panel">
          <div className="flex items-center justify-between border-b border-mars-border pb-2">
            <h3 className="font-bold text-white">COMPONENT FACTOR DECOMPOSITION</h3>
            <span className="text-[10px] text-slate-400">Weighted Contribution to Composite Score</span>
          </div>

          <div className="space-y-4">
            {/* Factor 1: Thermal Stress */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-300">
                <span className="font-semibold">1. Diurnal Thermal Stress (35% Weight)</span>
                <span className="text-mars-amber font-bold">{factors.thermal_stress.score} / 100</span>
              </div>
              <div className="w-full h-2.5 bg-mars-surface rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-amber-500 to-rose-500 rounded-full transition-all"
                  style={{ width: `${factors.thermal_stress.score}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>Metric: {factors.thermal_stress.metric}</span>
                <span>{factors.thermal_stress.rationale}</span>
              </div>
            </div>

            {/* Factor 2: Barometric Instability */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-300">
                <span className="font-semibold">2. Barometric Instability (25% Weight)</span>
                <span className="text-sky-400 font-bold">{factors.barometric_instability.score} / 100</span>
              </div>
              <div className="w-full h-2.5 bg-mars-surface rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-sky-500 to-blue-500 rounded-full transition-all"
                  style={{ width: `${factors.barometric_instability.score}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>Metric: {factors.barometric_instability.metric}</span>
                <span>{factors.barometric_instability.rationale}</span>
              </div>
            </div>

            {/* Factor 3: Anomaly Intensity */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-300">
                <span className="font-semibold">3. Anomaly Intensity (25% Weight)</span>
                <span className="text-mars-warning font-bold">{factors.anomaly_intensity.score} / 100</span>
              </div>
              <div className="w-full h-2.5 bg-mars-surface rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-yellow-500 to-amber-500 rounded-full transition-all"
                  style={{ width: `${factors.anomaly_intensity.score}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>Metric: {factors.anomaly_intensity.metric}</span>
                <span>{factors.anomaly_intensity.rationale}</span>
              </div>
            </div>

            {/* Factor 4: Seasonal Dust Forcing */}
            <div className="space-y-1.5">
              <div className="flex justify-between text-slate-300">
                <span className="font-semibold">4. Seasonal Perihelion Dust Forcing (15% Weight)</span>
                <span className="text-purple-400 font-bold">{factors.seasonal_dust_forcing.score} / 100</span>
              </div>
              <div className="w-full h-2.5 bg-mars-surface rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 rounded-full transition-all"
                  style={{ width: `${factors.seasonal_dust_forcing.score}%` }}
                />
              </div>
              <div className="flex justify-between text-[10px] text-slate-500">
                <span>Metric: {factors.seasonal_dust_forcing.metric}</span>
                <span>{factors.seasonal_dust_forcing.rationale}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Interactive Scenario Simulator (Directive 32) */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-6 space-y-4 font-mono text-xs shadow-panel">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-mars-border pb-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-mars-cyan" />
            <h3 className="font-bold text-white">SIMULATED WHAT-IF SCENARIO ANALYSIS</h3>
          </div>
          <span className="text-[10px] px-2 py-0.5 rounded bg-mars-surface border border-mars-border text-mars-amber">
            SIMULATED ANALYTICAL SCENARIO
          </span>
        </div>

        <p className="text-slate-300 font-sans text-xs">
          Explore hypothetical environmental perturbations (e.g. intensified temperature variability, sudden barometric drop, or global dust storm activation) to inspect sensitivity of the index.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-2">
          {/* Slider 1: Temp Multiplier */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-400">Thermal Swing Multiplier:</span>
              <span className="text-white font-bold">{tempMultiplier}x</span>
            </div>
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={tempMultiplier}
              onChange={(e) => setTempMultiplier(Number(e.target.value))}
              className="w-full accent-mars-amber cursor-pointer"
            />
          </div>

          {/* Slider 2: Pressure Drop */}
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-slate-400">Pressure Instability Delta:</span>
              <span className="text-white font-bold">+{pressureDrop} Pa/Sol</span>
            </div>
            <input
              type="range"
              min="0"
              max="35"
              step="1"
              value={pressureDrop}
              onChange={(e) => setPressureDrop(Number(e.target.value))}
              className="w-full accent-sky-400 cursor-pointer"
            />
          </div>

          {/* Toggle 3: Dust Storm */}
          <div className="flex items-center justify-between p-3 bg-mars-surface rounded border border-mars-border">
            <span className="text-slate-300">Inject Planetary Dust Storm:</span>
            <input
              type="checkbox"
              checked={dustStorm}
              onChange={(e) => setDustStorm(e.target.checked)}
              className="accent-mars-amber w-4 h-4 cursor-pointer"
            />
          </div>
        </div>

        <div className="flex items-center justify-between pt-3 border-t border-mars-border">
          <div className="flex items-center gap-3">
            <button
              onClick={runSimulation}
              disabled={simulating}
              className="px-4 py-2 rounded bg-mars-amber hover:bg-mars-rust text-white font-bold transition-all flex items-center gap-1.5"
            >
              <Play className="w-3.5 h-3.5" />
              <span>{simulating ? "COMPUTING..." : "RUN WHAT-IF SIMULATION"}</span>
            </button>
            <button
              onClick={resetSimulation}
              className="px-3 py-2 rounded bg-mars-surface border border-mars-border text-slate-300 hover:text-white"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>

          {simResult && (
            <div className="flex items-center gap-4 text-xs font-mono">
              <span className="text-slate-400">Simulated MECI:</span>
              <span className="text-2xl font-bold text-mars-amber">
                {simResult.simulated_meci}
              </span>
              <span className={`font-bold ${simResult.delta > 0 ? "text-rose-400" : "text-emerald-400"}`}>
                ({simResult.delta_description})
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
