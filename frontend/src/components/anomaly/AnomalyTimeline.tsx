import React, { useState, useEffect } from "react";
import { 
  AlertTriangle, 
  Play, 
  Filter, 
  Activity, 
  Sliders, 
  ShieldAlert,
  Flame,
  ArrowRight
} from "lucide-react";
import { AnomalyItem } from "../../lib/types";
import { api } from "../../lib/api";
import { EventReplay } from "./EventReplay";

export const AnomalyTimeline: React.FC = () => {
  const [anomalies, setAnomalies] = useState<AnomalyItem[]>([]);
  const [selectedSolForReplay, setSelectedSolForReplay] = useState<number | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>("ALL");
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    api.getAnomalies()
      .then((res) => {
        if (isMounted) {
          setAnomalies(res.multivariate_anomalies || []);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load anomalies:", err);
        setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  const filtered = anomalies.filter((a) => {
    if (severityFilter === "ALL") return true;
    return a.severity === severityFilter;
  });

  return (
    <div className="space-y-6">
      {/* Module Banner */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 04</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-mars-warning" />
            MARS ANOMALY INTELLIGENCE & TIMELINE
          </h2>
          <p className="text-xs text-slate-400">
            Multivariate Isolation Forest evaluating joint environmental states: diurnal thermal collapse, pressure surges, and dust lifting.
          </p>
        </div>

        {/* Severity Filter */}
        <div className="flex items-center gap-2 text-xs font-mono">
          <span className="text-slate-400">Severity:</span>
          {["ALL", "EXTREME", "HIGH", "MODERATE"].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2.5 py-1 rounded transition-colors ${
                severityFilter === sev
                  ? "bg-mars-amber text-white font-bold"
                  : "bg-mars-surface text-slate-400 border border-mars-border hover:text-white"
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      {/* Signature WOW Moment 1: Active Event Replay Container */}
      {selectedSolForReplay !== null && (
        <EventReplay
          targetSol={selectedSolForReplay}
          onClose={() => setSelectedSolForReplay(null)}
        />
      )}

      {/* Anomaly Timeline List (Directive 20) */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-5 space-y-4">
        <div className="flex items-center justify-between border-b border-mars-border pb-3">
          <h3 className="text-sm font-bold font-mono text-white flex items-center gap-2">
            <Activity className="w-4 h-4 text-mars-amber" />
            DETECTED MULTIVARIATE ANOMALY EVENTS ({filtered.length})
          </h3>
          <span className="text-[11px] font-mono text-slate-400">
            Algorithm: Isolation Forest (n_estimators=120, contamination=0.025)
          </span>
        </div>

        {loading ? (
          <div className="p-8 text-center font-mono text-xs text-slate-400">
            Running Multivariate Anomaly Detectors...
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center font-mono text-xs text-slate-400">
            No anomalies found matching current filter.
          </div>
        ) : (
          <div className="space-y-3">
            {filtered.map((item) => (
              <div
                key={item.sol}
                className="p-4 rounded-lg bg-mars-surface border border-mars-border hover:border-mars-amber transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 group"
              >
                <div className="space-y-1.5 flex-1">
                  <div className="flex flex-wrap items-center gap-3">
                    <span className="font-mono text-sm font-bold text-white">
                      Sol {item.sol}
                    </span>
                    <span className="font-mono text-xs text-slate-400">
                      {item.terrestrial_date}
                    </span>
                    <span
                      className={`font-mono text-[10px] px-2 py-0.5 rounded font-bold ${
                        item.severity === "EXTREME"
                          ? "bg-rose-500/20 text-rose-400 border border-rose-500/40"
                          : item.severity === "HIGH"
                          ? "bg-amber-500/20 text-amber-400 border border-amber-500/40"
                          : "bg-blue-500/20 text-blue-400 border border-blue-500/40"
                      }`}
                    >
                      {item.severity} SEVERITY
                    </span>
                    <span className="font-mono text-xs text-mars-cyan">
                      Anomaly Score: {item.anomaly_intensity}/100
                    </span>
                  </div>

                  {/* Primary Contributors */}
                  <div className="text-xs text-slate-300 font-sans">
                    <strong className="text-slate-400 font-mono text-[11px]">Primary Factor: </strong>
                    {item.primary_contributors.join("; ")}
                  </div>

                  {/* Telemetry Snapshot */}
                  <div className="flex flex-wrap items-center gap-4 text-xs font-mono text-slate-400 pt-1">
                    <span>Pressure: <strong className="text-white">{item.observed_values.pressure_pa} Pa</strong></span>
                    <span>Diurnal Swing: <strong className="text-mars-amber">Δ {item.observed_values.temp_amplitude_c} °C</strong></span>
                    <span>Max Temp: <strong className="text-rose-400">{item.observed_values.air_temp_max_c} °C</strong></span>
                    <span>Season: <strong className="text-slate-300">{item.observed_values.season}</strong></span>
                  </div>
                </div>

                {/* Launch Event Replay Button (Signature Interaction) */}
                <button
                  onClick={() => setSelectedSolForReplay(item.sol)}
                  className="px-3.5 py-2 rounded bg-mars-panel hover:bg-mars-amber text-slate-200 hover:text-white border border-mars-border group-hover:border-mars-amber font-mono text-xs font-bold transition-all flex items-center gap-1.5 whitespace-nowrap self-start md:self-center"
                >
                  <Play className="w-3.5 h-3.5 text-mars-cyan group-hover:text-white" />
                  <span>RECONSTRUCT EVENT</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
