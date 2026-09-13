import React, { useState, useEffect } from "react";
import { Layers, Activity, ShieldCheck, AlertCircle } from "lucide-react";
import { VerticalProfileData } from "../../lib/types";
import { api } from "../../lib/api";

export const VerticalProfileViewer: React.FC = () => {
  const [profiles, setProfiles] = useState<VerticalProfileData[]>([]);
  const [selectedIdx, setSelectedIdx] = useState<number>(0);
  const [activeVar, setActiveVar] = useState<"temperature_k" | "pressure_pa" | "dust_extinction_km_inv">("temperature_k");
  const [showUncertainty, setShowUncertainty] = useState<boolean>(true);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    api.getProfiles()
      .then((res) => {
        if (isMounted) {
          setProfiles(res.profiles);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load vertical profiles:", err);
        setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  const currentProfile = profiles[selectedIdx];
  const levels = currentProfile?.levels || [];

  // SVG dimensions for Altitude Profile (Altitude on Y-axis, Variable on X-axis)
  const svgWidth = 600;
  const svgHeight = 400;
  const padding = { top: 30, right: 30, bottom: 45, left: 60 };
  const plotWidth = svgWidth - padding.left - padding.right;
  const plotHeight = svgHeight - padding.top - padding.bottom;

  // Max altitude is 80 km
  const maxAlt = 80.0;
  const getY = (alt: number) => padding.top + plotHeight - (alt / maxAlt) * plotHeight;

  // X scale depends on active variable
  let minX = 100.0;
  let maxX = 260.0;
  let unitLabel = "Temperature (K)";

  if (activeVar === "pressure_pa") {
    minX = 0.01;
    maxX = 800.0;
    unitLabel = "Pressure (Pa)";
  } else if (activeVar === "dust_extinction_km_inv") {
    minX = 0.0;
    maxX = 0.025;
    unitLabel = "Dust Extinction (km⁻¹)";
  }

  const getX = (val: number) => {
    const range = Math.max(0.0001, maxX - minX);
    return padding.left + ((val - minX) / range) * plotWidth;
  };

  // Main Profile Path
  const profilePoints = levels.map((lvl) => ({
    x: getX(lvl[activeVar]),
    y: getY(lvl.altitude_km)
  }));

  const pathD = profilePoints.reduce((acc, pt, i) => {
    return i === 0 ? `M ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}` : `${acc} L ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`;
  }, "");

  // Uncertainty Polygon (for temperature)
  let uncertaintyPathD = "";
  if (showUncertainty && activeVar === "temperature_k" && levels.length > 0) {
    const upperPoints = levels.map((lvl) => ({
      x: getX(lvl.temperature_k + lvl.temperature_uncertainty_k),
      y: getY(lvl.altitude_km)
    }));
    const lowerPoints = levels.map((lvl) => ({
      x: getX(lvl.temperature_k - lvl.temperature_uncertainty_k),
      y: getY(lvl.altitude_km)
    })).reverse();

    const combined = [...upperPoints, ...lowerPoints];
    uncertaintyPathD = combined.reduce((acc, pt, i) => {
      return i === 0 ? `M ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}` : `${acc} L ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`;
    }, "") + " Z";
  }

  return (
    <div className="space-y-6">
      {/* Module Header */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 03</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Layers className="w-5 h-5 text-mars-amber" />
            ATMOSPHERIC SOUNDING & VERTICAL PROFILES
          </h2>
          <p className="text-xs text-slate-400">
            NASA MRO Mars Climate Sounder (MCS) Level 2 Derived Data Records: Limb soundings from 0 km to 80 km altitude.
          </p>
        </div>

        {/* Profile Selector */}
        <div className="flex items-center gap-2">
          <select
            value={selectedIdx}
            onChange={(e) => setSelectedIdx(Number(e.target.value))}
            className="px-3 py-1.5 bg-mars-surface border border-mars-border rounded text-xs font-mono text-white focus:outline-none focus:border-mars-cyan"
          >
            {profiles.map((p, idx) => (
              <option key={p.profile_id} value={idx}>
                {p.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Control Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 bg-mars-surface/70 border border-mars-border rounded-lg px-4 py-2.5 text-xs font-mono">
        <div className="flex items-center gap-2">
          <span className="text-slate-400">Variable:</span>
          <button
            onClick={() => setActiveVar("temperature_k")}
            className={`px-2.5 py-1 rounded transition-colors ${
              activeVar === "temperature_k" ? "bg-mars-amber text-white font-bold" : "bg-mars-dark text-slate-300 border border-mars-border"
            }`}
          >
            Temperature T(z)
          </button>
          <button
            onClick={() => setActiveVar("pressure_pa")}
            className={`px-2.5 py-1 rounded transition-colors ${
              activeVar === "pressure_pa" ? "bg-mars-cyan text-mars-darkest font-bold" : "bg-mars-dark text-slate-300 border border-mars-border"
            }`}
          >
            Pressure P(z)
          </button>
          <button
            onClick={() => setActiveVar("dust_extinction_km_inv")}
            className={`px-2.5 py-1 rounded transition-colors ${
              activeVar === "dust_extinction_km_inv" ? "bg-amber-400 text-mars-darkest font-bold" : "bg-mars-dark text-slate-300 border border-mars-border"
            }`}
          >
            Dust Opacity
          </button>
        </div>

        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer text-slate-300">
            <input
              type="checkbox"
              checked={showUncertainty}
              onChange={(e) => setShowUncertainty(e.target.checked)}
              className="accent-mars-amber"
            />
            <span>Show 1-σ Uncertainty Envelope</span>
          </label>
        </div>
      </div>

      {/* Vertical Chart & Scientific Commentary Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* SVG Altitude Profile Chart */}
        <div className="lg:col-span-2 bg-mars-panel border border-mars-border rounded-lg p-4 shadow-panel">
          <div className="flex justify-between items-center mb-2 px-2 text-xs font-mono">
            <span className="text-slate-300 font-bold">{currentProfile?.label}</span>
            <span className="text-mars-cyan">Orbit #{currentProfile?.orbit_number}</span>
          </div>

          <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-auto select-none">
            {/* Horizontal Altitude Grid Lines */}
            {[0, 20, 40, 60, 80].map((alt) => {
              const y = getY(alt);
              return (
                <g key={alt}>
                  <line x1={padding.left} y1={y} x2={svgWidth - padding.right} y2={y} stroke="#1e2e47" strokeDasharray="3 3" />
                  <text x={padding.left - 8} y={y + 4} textAnchor="end" className="text-[10px] fill-slate-500 font-mono">
                    {alt} km
                  </text>
                </g>
              );
            })}

            {/* Vertical Variable Ticks */}
            {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
              const x = padding.left + pct * plotWidth;
              const val = minX + pct * (maxX - minX);
              return (
                <g key={pct}>
                  <line x1={x} y1={padding.top + plotHeight} x2={x} y2={padding.top + plotHeight + 4} stroke="#2d4468" />
                  <text x={x} y={padding.top + plotHeight + 16} textAnchor="middle" className="text-[10px] fill-slate-400 font-mono">
                    {activeVar === "dust_extinction_km_inv" ? val.toFixed(4) : val.toFixed(0)}
                  </text>
                </g>
              );
            })}

            {/* Uncertainty Envelope Polygon */}
            {uncertaintyPathD && (
              <path d={uncertaintyPathD} fill="#e07a5f" fillOpacity="0.15" />
            )}

            {/* Profile Line */}
            <path
              d={pathD}
              fill="none"
              stroke="#e07a5f"
              strokeWidth="2.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />

            {/* Profile Points */}
            {profilePoints.map((pt, i) => (
              <circle
                key={i}
                cx={pt.x}
                cy={pt.y}
                r="3.5"
                fill="#38bdf8"
                stroke="#080d16"
                strokeWidth="1"
              />
            ))}

            {/* Y Axis Label */}
            <text
              x={15}
              y={svgHeight / 2}
              textAnchor="middle"
              transform={`rotate(-90 15 ${svgHeight / 2})`}
              className="text-xs fill-slate-400 font-mono"
            >
              Altitude above MOLA Aeroid (km)
            </text>

            {/* X Axis Label */}
            <text
              x={svgWidth / 2}
              y={svgHeight - 10}
              textAnchor="middle"
              className="text-xs fill-slate-400 font-mono"
            >
              {unitLabel}
            </text>
          </svg>
        </div>

        {/* Vertical Sounding Scientific Metadata Card */}
        <div className="bg-mars-panel border border-mars-border rounded-lg p-5 space-y-4 font-mono text-xs">
          <div className="flex items-center gap-2 text-mars-amber font-bold">
            <ShieldCheck className="w-4 h-4" />
            <span>MCS SOUNDING SPECIFICATIONS</span>
          </div>

          <div className="space-y-3">
            <div className="p-3 bg-mars-surface rounded border border-mars-border space-y-1">
              <span className="text-slate-500 text-[10px]">SPATIAL COORDINATES</span>
              <div className="text-white font-bold">
                Lat: {currentProfile?.latitude_deg}° | Lon: {currentProfile?.longitude_deg_east}° E
              </div>
              <div className="text-slate-400 text-[11px]">
                Solar Longitude: <span className="text-mars-cyan font-bold">{currentProfile?.solar_longitude_ls}°</span>
              </div>
            </div>

            <div className="p-3 bg-mars-surface rounded border border-mars-border space-y-1">
              <span className="text-slate-500 text-[10px]">HYDROSTATIC RETRIEVAL</span>
              <div className="text-white font-bold">25 Discrete Pressure Layers</div>
              <div className="text-slate-400 text-[11px]">
                Surface: ~{levels[0]?.pressure_pa.toFixed(0)} Pa → 80 km: {levels[levels.length - 1]?.pressure_pa.toFixed(3)} Pa
              </div>
            </div>

            <div className="p-3 bg-mars-surface rounded border border-mars-border space-y-1">
              <span className="text-slate-500 text-[10px]">MEASUREMENT UNCERTAINTY</span>
              <div className="text-white">Reported 1-σ: ±1.5 K to ±6.3 K</div>
              <p className="text-[11px] text-slate-400 font-sans mt-1">
                Uncertainty grows at higher altitudes as atmospheric CO2 density thins, lowering the mid-IR signal-to-noise ratio.
              </p>
            </div>

            <div className="p-3 bg-mars-surface/60 rounded border border-mars-border space-y-1 font-sans text-slate-300">
              <span className="font-mono text-mars-amber text-[10px] font-bold block">PLANETARY SCIENCE CONTEXT</span>
              <p className="text-[11px] leading-relaxed">
                During dust storm events, solar absorption by suspended dust particles creates pronounced mid-altitude heating layers,
                inverting the standard adiabatic lapse rate between 20 km and 50 km altitude.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
