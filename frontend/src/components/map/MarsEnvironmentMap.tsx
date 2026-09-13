import React, { useState } from "react";
import { MapPin, Globe2, Layers, Info, Compass, Shield } from "lucide-react";

interface SiteLocation {
  id: string;
  name: string;
  type: "rover" | "lander" | "feature";
  lat: number;
  lon: number;
  elevation_km: number;
  mission: string;
  instrument: string;
  status: string;
  key_findings: string;
}

const MARS_SITES: SiteLocation[] = [
  {
    id: "gale",
    name: "Gale Crater (Aeolis Palus)",
    type: "rover",
    lat: -4.5895,
    lon: 137.4417,
    elevation_km: -4.5,
    mission: "Curiosity (MSL)",
    instrument: "REMS (Rover Environmental Monitoring Station)",
    status: "Active (Sol 1 — Present)",
    key_findings: "4,700+ Sols of continuous boundary layer meteorological monitoring. Regular diurnal pressure waves and seasonal CO2 condensation cycle."
  },
  {
    id: "elysium",
    name: "Elysium Planitia",
    type: "lander",
    lat: 4.5024,
    lon: 135.6234,
    elevation_km: -2.6,
    mission: "InSight Lander",
    instrument: "TWINS / APSS (Auxiliary Payload Sensor Suite)",
    status: "Completed (Sol 0 — 1366)",
    key_findings: "High-precision micro-barometer detected thousands of atmospheric vortices (dust devils) and acoustic gravity waves."
  },
  {
    id: "jezero",
    name: "Jezero Crater",
    type: "rover",
    lat: 18.38,
    lon: 77.58,
    elevation_km: -2.5,
    mission: "Perseverance (Mars 2020)",
    instrument: "MEDA (Mars Environmental Dynamics Analyzer)",
    status: "Active (Sol 0 — Present)",
    key_findings: "High-frequency wind speed, thermal radiation balance, and dust optical depth in paleo-lake basin."
  },
  {
    id: "olympus",
    name: "Olympus Mons (Shield Volcano)",
    type: "feature",
    lat: 18.65,
    lon: 226.2,
    elevation_km: 21.2,
    mission: "Planetary Feature",
    instrument: "MRO Mars Climate Sounder / MOLA",
    status: "Permanent Geologic Feature",
    key_findings: "Tallest planetary volcano in the solar system. Peak extends above 95% of the Martian atmospheric column (~30 Pa pressure)."
  },
  {
    id: "valles",
    name: "Valles Marineris (Chasma)",
    type: "feature",
    lat: -14.0,
    lon: 300.8,
    elevation_km: -7.0,
    mission: "Planetary Feature",
    instrument: "MRO MCS Atmospheric Sounder",
    status: "Permanent Geologic Feature",
    key_findings: "Deep tectonic rift canyon system. Canyon floor experiences localized high-density morning atmospheric water-ice fogs."
  }
];

export const MarsEnvironmentMap: React.FC = () => {
  const [selectedSite, setSelectedSite] = useState<SiteLocation>(MARS_SITES[0]);

  // Coordinate projection to SVG Canvas (Equirectangular Cylindrical projection)
  // Longitude 0 to 360 -> X: 0 to 800
  // Latitude -90 to +90 -> Y: 400 to 0
  const svgWidth = 800;
  const svgHeight = 400;

  const projectX = (lon: number) => {
    const normLon = ((lon % 360) + 360) % 360;
    return (normLon / 360.0) * svgWidth;
  };

  const projectY = (lat: number) => {
    return svgHeight / 2 - (lat / 90.0) * (svgHeight / 2);
  };

  return (
    <div className="space-y-6">
      {/* Module Banner */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 05</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Globe2 className="w-5 h-5 text-mars-amber" />
            MARS SPATIAL ENVIRONMENT & LANDING SITES
          </h2>
          <p className="text-xs text-slate-400">
            Spatial distribution of NASA surface stations and topographic elevation baselines (MOLA Aeroid Datum).
          </p>
        </div>

        <div className="flex items-center gap-3 font-mono text-xs text-slate-400">
          <span>Datum: <strong className="text-white">MOLA Aeroid (0 km)</strong></span>
          <span>Planet Radius: <strong className="text-mars-cyan">3,389.5 km</strong></span>
        </div>
      </div>

      {/* Interactive Map Canvas */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 shadow-panel space-y-3">
        <div className="flex justify-between items-center px-1 text-xs font-mono text-slate-400">
          <span className="text-white font-bold">Martian Surface Coordinates (IAU Planetocentric 2000)</span>
          <span>Click any marker to inspect elevation & station findings</span>
        </div>

        <div className="relative rounded-lg overflow-hidden border border-mars-border bg-mars-darkest">
          <svg viewBox={`0 0 ${svgWidth} ${svgHeight}`} className="w-full h-auto select-none">
            {/* Background Texture & Latitude/Longitude Grid */}
            <rect width={svgWidth} height={svgHeight} fill="#06090e" />
            
            {/* Latitude Grid Lines (-60, -30, 0, +30, +60) */}
            {[-60, -30, 0, 30, 60].map((lat) => {
              const y = projectY(lat);
              return (
                <g key={lat}>
                  <line x1={0} y1={y} x2={svgWidth} y2={y} stroke="#142033" strokeDasharray="4 4" />
                  <text x={10} y={y - 4} className="text-[9px] fill-slate-600 font-mono">
                    {lat > 0 ? `+${lat}° N` : lat === 0 ? "Equator" : `${lat}° S`}
                  </text>
                </g>
              );
            })}

            {/* Longitude Grid Lines (0, 90, 180, 270) */}
            {[0, 90, 180, 270].map((lon) => {
              const x = projectX(lon);
              return (
                <g key={lon}>
                  <line x1={x} y1={0} x2={x} y2={svgHeight} stroke="#142033" strokeDasharray="4 4" />
                  <text x={x + 4} y={svgHeight - 10} className="text-[9px] fill-slate-600 font-mono">
                    {lon}° E
                  </text>
                </g>
              );
            })}

            {/* Simulated Martian Terrain Contours */}
            <path
              d="M 120 180 Q 240 120 380 190 T 600 240 Q 720 280 780 210"
              fill="none"
              stroke="#e07a5f"
              strokeOpacity="0.15"
              strokeWidth="1.5"
            />
            <path
              d="M 50 240 Q 180 310 320 280 T 540 320 Q 670 300 790 330"
              fill="none"
              stroke="#e07a5f"
              strokeOpacity="0.12"
              strokeWidth="1.5"
            />

            {/* Site Markers */}
            {MARS_SITES.map((site) => {
              const x = projectX(site.lon);
              const y = projectY(site.lat);
              const isSelected = selectedSite.id === site.id;

              return (
                <g
                  key={site.id}
                  onClick={() => setSelectedSite(site)}
                  className="cursor-pointer group"
                >
                  {/* Ping Ring for Selected */}
                  {isSelected && (
                    <circle cx={x} cy={y} r="14" fill="none" stroke="#e07a5f" strokeWidth="1.5" strokeOpacity="0.8" className="animate-ping" />
                  )}

                  {/* Marker Outer Circle */}
                  <circle
                    cx={x}
                    cy={y}
                    r={isSelected ? "8" : "6"}
                    fill={site.type === "rover" ? "#38bdf8" : site.type === "lander" ? "#34d399" : "#e07a5f"}
                    stroke="#04070c"
                    strokeWidth="2"
                    className="transition-all"
                  />

                  {/* Label */}
                  <text
                    x={x}
                    y={y - 12}
                    textAnchor="middle"
                    className={`text-[10px] font-mono font-bold transition-all ${
                      isSelected ? "fill-mars-amber text-xs" : "fill-slate-300 group-hover:fill-white"
                    }`}
                  >
                    {site.name}
                  </text>
                </g>
              );
            })}
          </svg>
        </div>
      </div>

      {/* Selected Site Details Inspector */}
      {selectedSite && (
        <div className="bg-mars-panel border border-mars-border rounded-lg p-5 space-y-4 font-mono text-xs shadow-panel">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 border-b border-mars-border pb-3">
            <div>
              <span className="text-mars-cyan text-[10px] uppercase">{selectedSite.type} STATION</span>
              <h3 className="text-base font-bold text-white">{selectedSite.name}</h3>
            </div>
            <div className="flex items-center gap-2">
              <span className="px-2 py-0.5 rounded bg-mars-surface border border-mars-border text-slate-300">
                Status: <strong className="text-emerald-400">{selectedSite.status}</strong>
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-mars-surface rounded border border-mars-border">
              <span className="text-slate-500 text-[10px]">GEOGRAPHIC COORDINATES</span>
              <div className="text-white font-bold mt-0.5">
                {selectedSite.lat}° N, {selectedSite.lon}° E
              </div>
            </div>

            <div className="p-3 bg-mars-surface rounded border border-mars-border">
              <span className="text-slate-500 text-[10px]">MOLA ELEVATION</span>
              <div className="text-white font-bold mt-0.5">
                {selectedSite.elevation_km > 0 ? `+${selectedSite.elevation_km}` : selectedSite.elevation_km} km
              </div>
              <div className="text-[10px] text-slate-400">Relative to Mean Aeroid</div>
            </div>

            <div className="p-3 bg-mars-surface rounded border border-mars-border">
              <span className="text-slate-500 text-[10px]">PRIMARY INSTRUMENT</span>
              <div className="text-mars-cyan font-bold mt-0.5">{selectedSite.instrument}</div>
            </div>
          </div>

          <div className="p-3 bg-mars-surface/60 rounded border border-mars-border space-y-1">
            <span className="text-mars-amber text-[10px] font-bold">ATMOSPHERIC CONTEXT & SCIENTIFIC FINDINGS</span>
            <p className="text-slate-200 font-sans text-xs leading-relaxed">
              {selectedSite.key_findings}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};
