import React from "react";
import { 
  Activity, 
  Thermometer, 
  Gauge, 
  AlertTriangle, 
  ShieldAlert, 
  Database, 
  ArrowUpRight,
  Sun,
  Flame,
  Sparkles
} from "lucide-react";
import { MissionOverviewData } from "../../lib/types";

interface MissionOverviewProps {
  data: MissionOverviewData | null;
  onNavigate: (tabId: string) => void;
}

export const MissionOverview: React.FC<MissionOverviewProps> = ({ data, onNavigate }) => {
  if (!data) {
    return (
      <div className="p-8 text-center font-mono text-xs text-slate-400 bg-slate-900/60 backdrop-blur-md border border-slate-800/80 rounded-xl shadow-lg">
        Loading Martian Environmental Telemetry...
      </div>
    );
  }

  const meci = data.current_meci;

  return (
    <div className="space-y-5">
      {/* 1. KPI Metrics Grid — first element, directly below nav */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* KPI 1: Observations */}
        <div className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-cyan-400 hover:border-slate-700/80 rounded-xl p-3.5 transition-all duration-300 ease-in-out hover:translate-y-[-2px] shadow-lg hover:shadow-cyan-500/10">
          <div className="text-[11px] text-slate-400 font-mono font-semibold tracking-wider uppercase flex items-center justify-between">
            <span>NASA OBSERVATIONS</span>
            <Database className="w-3.5 h-3.5 text-cyan-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-2xl font-black font-mono text-white mt-1.5 tracking-tight drop-shadow-sm">
            {data.total_observations.toLocaleString()}
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-1 font-medium tracking-wide uppercase">Continuous Records</div>
        </div>

        {/* KPI 2: Recorded Sols */}
        <div className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-amber-400 hover:border-slate-700/80 rounded-xl p-3.5 transition-all duration-300 ease-in-out hover:translate-y-[-2px] shadow-lg hover:shadow-amber-500/10">
          <div className="text-[11px] text-slate-400 font-mono font-semibold tracking-wider uppercase flex items-center justify-between">
            <span>RECORDED SOLS</span>
            <Sun className="w-3.5 h-3.5 text-amber-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-2xl font-black font-mono text-amber-400 mt-1.5 tracking-tight drop-shadow-sm">
            Sol {data.total_sols_recorded}
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-1 font-medium tracking-wide uppercase">2012 — 2026 UTC</div>
        </div>

        {/* KPI 3: Surface Pressure */}
        <div className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-sky-400 hover:border-slate-700/80 rounded-xl p-3.5 transition-all duration-300 ease-in-out hover:translate-y-[-2px] shadow-lg hover:shadow-sky-500/10">
          <div className="text-[11px] text-slate-400 font-mono font-semibold tracking-wider uppercase flex items-center justify-between">
            <span>SURFACE PRESSURE</span>
            <Gauge className="w-3.5 h-3.5 text-sky-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-2xl font-black font-mono text-cyan-300 mt-1.5 tracking-tight drop-shadow-sm">
            {data.latest_pressure_pa ? `${data.latest_pressure_pa} Pa` : "N/A"}
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-1 font-medium tracking-wide uppercase">Gale Crater Datum</div>
        </div>

        {/* KPI 4: Diurnal Thermal Swing */}
        <div className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-rose-400 hover:border-slate-700/80 rounded-xl p-3.5 transition-all duration-300 ease-in-out hover:translate-y-[-2px] shadow-lg hover:shadow-rose-500/10">
          <div className="text-[11px] text-slate-400 font-mono font-semibold tracking-wider uppercase flex items-center justify-between">
            <span>DIURNAL SWING</span>
            <Thermometer className="w-3.5 h-3.5 text-rose-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-2xl font-black font-mono text-rose-300 mt-1.5 tracking-tight drop-shadow-sm">
            {data.latest_temp_amplitude_c ? `Δ ${data.latest_temp_amplitude_c} °C` : "N/A"}
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-1 font-medium tracking-wide uppercase">
            {data.latest_temp_min_c}°C to {data.latest_temp_max_c}°C
          </div>
        </div>

        {/* KPI 5: Anomalies Detected */}
        <div className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-amber-400 hover:border-slate-700/80 rounded-xl p-3.5 transition-all duration-300 ease-in-out hover:translate-y-[-2px] shadow-lg hover:shadow-amber-500/10">
          <div className="text-[11px] text-slate-400 font-mono font-semibold tracking-wider uppercase flex items-center justify-between">
            <span>ANOMALIES</span>
            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-2xl font-black font-mono text-amber-300 mt-1.5 tracking-tight drop-shadow-sm">
            {data.anomalies_detected_count}
          </div>
          <div className="text-[10px] text-slate-400 font-mono mt-1 font-medium tracking-wide uppercase">Isolation Forest Flags</div>
        </div>

        {/* KPI 6: Challenge Index */}
        <div 
          className="group relative bg-slate-900/60 backdrop-blur-md border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-mars-amber hover:border-slate-700/80 rounded-xl p-3.5 cursor-pointer transition-all duration-300 ease-in-out hover:translate-y-[-2px] shadow-lg hover:shadow-orange-500/10"
          onClick={() => onNavigate("meci")}
        >
          <div className="text-[11px] text-slate-400 font-mono font-semibold tracking-wider uppercase flex items-center justify-between">
            <span>CHALLENGE INDEX</span>
            <ShieldAlert className="w-3.5 h-3.5 text-mars-rust group-hover:scale-110 transition-transform" />
          </div>
          <div className="text-2xl font-black font-mono text-mars-amber mt-1.5 tracking-tight flex items-baseline gap-1 drop-shadow-sm">
            <span>{meci?.index_score}</span>
            <span className="text-xs font-semibold text-slate-400">/100</span>
          </div>
          <div className="text-[10px] font-mono text-amber-300 mt-1 font-bold tracking-wide uppercase">
            {meci?.classification}
          </div>
        </div>
      </div>

      {/* 2. Main Analytics & Launchpad Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Environmental Indicators Card */}
        <div className="lg:col-span-2 bg-slate-900/60 backdrop-blur-md border border-slate-800/80 rounded-xl p-4 space-y-4 shadow-lg">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-3">
            <h2 className="text-xs font-bold font-mono text-white flex items-center gap-2 tracking-wider uppercase">
              <Activity className="w-4 h-4 text-cyan-400" />
              AUTHENTIC MARTIAN ENVIRONMENTAL STATE
            </h2>
            <span className="text-xs font-mono text-slate-300 tracking-wider">
              Solar Longitude: <span className="text-cyan-300 font-bold">{data.latest_solar_longitude_ls}°</span>
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs font-mono">
            <div className="group p-3.5 bg-slate-950/50 rounded-lg border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-amber-400/80 hover:border-slate-700/80 space-y-2 transition-all duration-300 ease-in-out hover:translate-y-[-2px]">
              <div className="text-slate-300 font-semibold flex items-center gap-2 tracking-wider uppercase text-[11px]">
                <Sun className="w-3.5 h-3.5 text-amber-400" />
                <span>Martian Season & Orbit</span>
              </div>
              <div className="text-sm font-bold text-white tracking-wide">{data.latest_season}</div>
              <p className="text-[11px] text-slate-400 font-sans leading-relaxed">
                Governed by orbital eccentricity (e = 0.0934), driving a 45% insolation delta between aphelion and perihelion.
              </p>
            </div>

            <div className="group p-3.5 bg-slate-950/50 rounded-lg border border-slate-800/80 border-t-2 border-t-transparent hover:border-t-rose-400/80 hover:border-slate-700/80 space-y-2 transition-all duration-300 ease-in-out hover:translate-y-[-2px]">
              <div className="text-slate-300 font-semibold flex items-center gap-2 tracking-wider uppercase text-[11px]">
                <Flame className="w-3.5 h-3.5 text-rose-400" />
                <span>Boundary Layer Thermal Stress</span>
              </div>
              <div className="text-sm font-bold text-rose-300 tracking-wide">
                Daily Range: Δ {data.latest_temp_amplitude_c} °C
              </div>
              <p className="text-[11px] text-slate-400 font-sans leading-relaxed">
                Low atmospheric density (~1% Earth) yields rapid radiative cooling and sharp diurnal thermal boundary waves.
              </p>
            </div>
          </div>

          <div className="p-3 bg-slate-950/40 rounded-lg border border-slate-800/70 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2 text-slate-300 text-[11px] font-mono">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
              <span>Baseline Stations: Curiosity (Gale Crater, -4.5 km) & InSight (Elysium, -2.6 km)</span>
            </div>
            <button
              onClick={() => onNavigate("explorer")}
              className="text-cyan-400 hover:text-cyan-300 font-mono text-xs font-semibold tracking-wider uppercase shrink-0 transition-colors flex items-center gap-1 group"
            >
              <span>Open Time Series</span>
              <ArrowUpRight className="w-3 h-3 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
            </button>
          </div>
        </div>

        {/* Quick Launchpad to Core Intelligence Modules */}
        <div className="bg-slate-900/60 backdrop-blur-md border border-slate-800/80 rounded-xl p-4 space-y-3 shadow-lg">
          <div className="flex items-center justify-between border-b border-slate-800/80 pb-2.5">
            <h2 className="text-xs font-bold font-mono text-white tracking-wider uppercase flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-mars-amber" />
              <span>INTELLIGENCE MODULES</span>
            </h2>
            <span className="text-[10px] text-slate-400 font-mono tracking-wider uppercase">10 Modules</span>
          </div>
          
          <div className="space-y-2">
            {[
              { id: "explorer", label: "Multi-Mission Explorer", desc: "4,700+ Sols of observations & tables" },
              { id: "atmospheric", label: "Atmospheric & Altitude Profiles", desc: "MRO MCS vertical limb sounding" },
              { id: "anomaly", label: "Anomaly Timeline & Event Replay", desc: "Reconstruct Mars dust & pressure events" },
              { id: "meci", label: "Environmental Challenge Index", desc: "0-100 volatility metric & What-If tool" },
              { id: "model", label: "ML Model Lab", desc: "Baseline vs Random Forest evaluation" },
              { id: "ai", label: "Mars Grounded AI Scientist", desc: "Evidence-linked planetary query assistant" },
            ].map((m) => (
              <div
                key={m.id}
                onClick={() => onNavigate(m.id)}
                className="p-2.5 rounded-lg bg-slate-950/50 hover:bg-slate-800/70 cursor-pointer border border-slate-800/80 hover:border-slate-700/90 border-t-2 border-t-transparent hover:border-t-cyan-400/80 flex items-center justify-between group transition-all duration-300 ease-in-out hover:translate-y-[-2px]"
              >
                <div>
                  <div className="text-xs font-semibold text-slate-200 group-hover:text-white transition-colors font-sans">{m.label}</div>
                  <div className="text-[11px] text-slate-400 group-hover:text-slate-300 transition-colors font-sans">{m.desc}</div>
                </div>
                <ArrowUpRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-cyan-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-all shrink-0 ml-2" />
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
