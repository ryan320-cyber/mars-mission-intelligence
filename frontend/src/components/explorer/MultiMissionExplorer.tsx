import React, { useState, useEffect } from "react";
import { 
  Compass, 
  Download, 
  Filter, 
  Layers, 
  Search, 
  Calendar, 
  AlertCircle,
  Eye,
  SlidersHorizontal,
  FileSpreadsheet
} from "lucide-react";
import { ObservationRecord, ObservationsResponse } from "../../lib/types";
import { api } from "../../lib/api";
import { ScientificTimeSeries } from "../charts/ScientificTimeSeries";

export const MultiMissionExplorer: React.FC = () => {
  const [mission, setMission] = useState<string>("curiosity");
  const [dataResponse, setDataResponse] = useState<ObservationsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  
  // Controls
  const [selectedVariable, setSelectedVariable] = useState<string>("pressure_pa");
  const [normalized, setNormalized] = useState<boolean>(false);
  const [searchSol, setSearchSol] = useState<string>("");
  const [selectedObs, setSelectedObs] = useState<ObservationRecord | null>(null);
  const [page, setPage] = useState<number>(0);
  const pageSize = 15;

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    api.getObservations(mission, 450)
      .then((res) => {
        if (isMounted) {
          setDataResponse(res);
          setLoading(false);
          setPage(0);
        }
      })
      .catch((err) => {
        console.error("Failed to load observations:", err);
        setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [mission]);

  const observations = dataResponse?.observations || [];

  // Series configs based on mission
  const seriesConfigs = mission === "curiosity" ? [
    { key: "pressure_pa" as keyof ObservationRecord, label: "Pressure", unit: "Pa", color: "#38bdf8" },
    { key: "air_temp_max_c" as keyof ObservationRecord, label: "Max Air Temp", unit: "°C", color: "#f43f5e" },
    { key: "air_temp_min_c" as keyof ObservationRecord, label: "Min Air Temp", unit: "°C", color: "#3b82f6" },
    { key: "temp_amplitude_c" as keyof ObservationRecord, label: "Diurnal Swing", unit: "°C", color: "#e07a5f" },
  ] : [
    { key: "pressure_pa" as keyof ObservationRecord, label: "Pressure", unit: "Pa", color: "#38bdf8" },
    { key: "air_temp_mean_c" as keyof ObservationRecord, label: "Mean Air Temp", unit: "°C", color: "#e07a5f" },
    { key: "wind_speed_mean_ms" as keyof ObservationRecord, label: "Wind Speed", unit: "m/s", color: "#34d399" },
  ];

  // Filtered table rows
  const filteredRows = observations.filter((obs) => {
    if (!searchSol) return true;
    return obs.sol.toString().includes(searchSol) || obs.terrestrial_date.includes(searchSol);
  });

  const paginatedRows = filteredRows.slice(page * pageSize, (page + 1) * pageSize);
  const totalPages = Math.ceil(filteredRows.length / pageSize);

  const handleExportCSV = () => {
    const baseUrl = import.meta.env.VITE_API_URL || 'https://mars-mission-intelligence3.vercel.app';
    window.open(`${baseUrl}/api/export?mission=${mission}&format=csv`, "_blank");
  };

  return (
    <div className="space-y-6">
      {/* Top Header & Mission Switcher (Directive 10) */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-mars-panel border border-mars-border rounded-lg p-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 02</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-mars-amber" />
            MULTI-MISSION MARS DATA EXPLORER
          </h2>
          <p className="text-xs text-slate-400">
            Select authentic planetary mission telemetry and inspect time-series and tabular observations.
          </p>
        </div>

        {/* Mission Switcher Buttons */}
        <div className="flex items-center gap-2 font-mono text-xs">
          <button
            onClick={() => setMission("curiosity")}
            className={`px-3 py-1.5 rounded transition-all ${
              mission === "curiosity"
                ? "bg-mars-surface border border-mars-amber text-mars-amber font-bold shadow-glow-amber"
                : "bg-mars-dark text-slate-400 border border-mars-border hover:text-white"
            }`}
          >
            Curiosity (Gale Crater)
          </button>
          <button
            onClick={() => setMission("insight")}
            className={`px-3 py-1.5 rounded transition-all ${
              mission === "insight"
                ? "bg-mars-surface border border-mars-cyan text-mars-cyan font-bold shadow-glow-cyan"
                : "bg-mars-dark text-slate-400 border border-mars-border hover:text-white"
            }`}
          >
            InSight (Elysium Planitia)
          </button>
        </div>
      </div>

      {/* Chart Controls Bar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-mars-surface/70 border border-mars-border rounded-lg px-4 py-2 text-xs font-mono">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-slate-300">
            <SlidersHorizontal className="w-3.5 h-3.5 text-mars-cyan" />
            <span>Mode:</span>
          </div>
          <button
            onClick={() => setNormalized(!normalized)}
            className={`px-2 py-1 rounded transition-colors ${
              normalized ? "bg-mars-cyan text-mars-darkest font-bold" : "bg-mars-dark text-slate-300 border border-mars-border"
            }`}
          >
            {normalized ? "Normalized [0–1]" : "Standard Units"}
          </button>
        </div>

        <div className="flex items-center gap-4 text-slate-400">
          <span>Observed Points: <strong className="text-white">{dataResponse?.returned_points || 0}</strong></span>
          <span>Sensor Gaps: <strong className="text-rose-400">{dataResponse?.sensor_gaps.length || 0}</strong></span>
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-1 px-2.5 py-1 rounded bg-mars-panel hover:bg-mars-surface text-slate-300 hover:text-white border border-mars-border transition-colors"
          >
            <Download className="w-3 h-3 text-mars-amber" />
            <span>Export CSV</span>
          </button>
        </div>
      </div>

      {/* Interactive Time-Series Chart */}
      {loading ? (
        <div className="h-64 bg-mars-panel border border-mars-border rounded-lg flex items-center justify-center font-mono text-xs text-slate-400">
          Loading Mission Time-Series Telemetry...
        </div>
      ) : (
        <ScientificTimeSeries
          data={observations}
          seriesConfigs={seriesConfigs}
          sensorGaps={dataResponse?.sensor_gaps}
          normalized={normalized}
          height={330}
        />
      )}

      {/* Advanced Observations Table (Directive 56) */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="w-4 h-4 text-mars-cyan" />
            <h3 className="text-sm font-bold font-mono text-white">
              AUTHENTIC OBSERVATIONS REGISTRY
            </h3>
            <span className="text-xs font-mono text-slate-400">
              ({filteredRows.length} Sols Matching)
            </span>
          </div>

          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
              <input
                type="text"
                value={searchSol}
                onChange={(e) => setSearchSol(e.target.value)}
                placeholder="Search Sol or Date..."
                className="pl-8 pr-3 py-1 bg-mars-surface border border-mars-border rounded text-xs text-white placeholder-slate-500 font-mono focus:outline-none focus:border-mars-cyan"
              />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead className="bg-mars-surface text-slate-400 border-b border-mars-border uppercase text-[10px]">
              <tr>
                <th className="py-2.5 px-3">Sol</th>
                <th className="py-2.5 px-3">Earth Date</th>
                <th className="py-2.5 px-3">Ls (°)</th>
                <th className="py-2.5 px-3">Pressure (Pa)</th>
                <th className="py-2.5 px-3">Max Temp (°C)</th>
                <th className="py-2.5 px-3">Min Temp (°C)</th>
                <th className="py-2.5 px-3">Diurnal Swing</th>
                <th className="py-2.5 px-3">Opacity</th>
                <th className="py-2.5 px-3 text-right">Detail</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-mars-border/40 text-slate-300">
              {paginatedRows.map((row) => (
                <tr
                  key={row.sol}
                  onClick={() => setSelectedObs(row)}
                  className="hover:bg-mars-surface/60 cursor-pointer transition-colors"
                >
                  <td className="py-2 px-3 font-bold text-mars-amber">Sol {row.sol}</td>
                  <td className="py-2 px-3 text-slate-400">{row.terrestrial_date}</td>
                  <td className="py-2 px-3 text-mars-cyan">{row.solar_longitude_ls ?? "--"}°</td>
                  <td className="py-2 px-3">{row.pressure_pa ?? "--"}</td>
                  <td className="py-2 px-3 text-rose-400">{row.air_temp_max_c ?? "--"}</td>
                  <td className="py-2 px-3 text-sky-400">{row.air_temp_min_c ?? "--"}</td>
                  <td className="py-2 px-3 text-slate-300">{row.temp_amplitude_c ? `Δ ${row.temp_amplitude_c}` : "--"}</td>
                  <td className="py-2 px-3">
                    <span className="px-1.5 py-0.5 rounded bg-mars-surface text-[10px] text-slate-400 border border-mars-border">
                      {row.atmospheric_opacity || "Sunny"}
                    </span>
                  </td>
                  <td className="py-2 px-3 text-right">
                    <Eye className="w-3.5 h-3.5 text-slate-400 hover:text-mars-cyan inline" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between pt-2 border-t border-mars-border text-xs font-mono text-slate-400">
          <span>Page {page + 1} of {Math.max(1, totalPages)}</span>
          <div className="flex items-center gap-2">
            <button
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
              className="px-2.5 py-1 rounded bg-mars-surface border border-mars-border disabled:opacity-30 hover:text-white"
            >
              Previous
            </button>
            <button
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
              className="px-2.5 py-1 rounded bg-mars-surface border border-mars-border disabled:opacity-30 hover:text-white"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      {/* Observation Detail Modal (Directive 55) */}
      {selectedObs && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-mars-panel border border-mars-border rounded-xl max-w-lg w-full p-6 space-y-4 shadow-panel font-mono text-xs">
            <div className="flex items-center justify-between border-b border-mars-border pb-3">
              <div>
                <span className="text-mars-cyan text-[10px]">VERIFIED NASA OBSERVATION</span>
                <h3 className="text-lg font-bold text-white">Sol {selectedObs.sol} Telemetry</h3>
              </div>
              <button
                onClick={() => setSelectedObs(null)}
                className="text-slate-400 hover:text-white text-lg font-bold px-2"
              >
                ✕
              </button>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-400 text-[10px]">TERRESTRIAL DATE</span>
                <div className="text-sm font-bold text-white">{selectedObs.terrestrial_date}</div>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-400 text-[10px]">SOLAR LONGITUDE (Ls)</span>
                <div className="text-sm font-bold text-mars-cyan">{selectedObs.solar_longitude_ls}°</div>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-400 text-[10px]">ATMOSPHERIC PRESSURE</span>
                <div className="text-sm font-bold text-white">{selectedObs.pressure_pa} Pa</div>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-400 text-[10px]">DIURNAL THERMAL SWING</span>
                <div className="text-sm font-bold text-mars-amber">Δ {selectedObs.temp_amplitude_c} °C</div>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-400 text-[10px]">MAX AIR TEMPERATURE</span>
                <div className="text-sm font-bold text-rose-400">{selectedObs.air_temp_max_c} °C</div>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-400 text-[10px]">MIN AIR TEMPERATURE</span>
                <div className="text-sm font-bold text-sky-400">{selectedObs.air_temp_min_c} °C</div>
              </div>
            </div>

            <div className="p-3 bg-mars-surface/60 rounded border border-mars-border text-[11px] space-y-1">
              <div className="text-slate-400">DATA PROVENANCE</div>
              <div className="text-white">Mission: {selectedObs.mission} | Site: {selectedObs.site}</div>
              <div className="text-slate-500">{selectedObs.data_source}</div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setSelectedObs(null)}
                className="px-4 py-1.5 rounded bg-mars-amber text-white font-bold"
              >
                Close Inspector
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
