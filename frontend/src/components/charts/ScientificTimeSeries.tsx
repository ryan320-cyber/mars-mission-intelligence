import React, { useState, useMemo, useRef, useCallback } from "react";
import { ObservationRecord, SensorGap } from "../../lib/types";

interface SeriesConfig {
  key: keyof ObservationRecord;
  label: string;
  unit: string;
  color: string;
}

interface ScientificTimeSeriesProps {
  data: ObservationRecord[];
  seriesConfigs: SeriesConfig[];
  sensorGaps?: SensorGap[];
  height?: number;
  highlightSols?: number[];
  normalized?: boolean;
}

// O(log N) binary search for instant interactive hover lookups
function findClosestPointIdx(pts: ObservationRecord[], targetSol: number): number {
  if (pts.length === 0) return 0;
  let low = 0;
  let high = pts.length - 1;
  while (low <= high) {
    const mid = (low + high) >> 1;
    if (pts[mid].sol === targetSol) return mid;
    if (pts[mid].sol < targetSol) low = mid + 1;
    else high = mid - 1;
  }
  if (low >= pts.length) return pts.length - 1;
  if (high < 0) return 0;
  return Math.abs(pts[low].sol - targetSol) < Math.abs(pts[high].sol - targetSol) ? low : high;
}

export const ScientificTimeSeries: React.FC<ScientificTimeSeriesProps> = ({
  data,
  seriesConfigs,
  sensorGaps = [],
  height = 320,
  highlightSols = [],
  normalized = false
}) => {
  const [hoveredIdx, setHoveredIdx] = useState<number | null>(null);
  const rafId = useRef<number | null>(null);

  // Filter valid data points
  const points = useMemo(() => {
    return data.filter((d) => d.sol !== undefined && d.sol !== null);
  }, [data]);

  // Compute Scales
  const bounds = useMemo(() => {
    if (points.length === 0) return { minSol: 0, maxSol: 1, minVal: 0, maxVal: 1, seriesBounds: {} };
    const minSol = points[0].sol;
    const maxSol = points[points.length - 1].sol;

    const seriesBounds: Record<string, { min: number; max: number }> = {};
    let overallMin = Infinity;
    let overallMax = -Infinity;

    seriesConfigs.forEach((cfg) => {
      const vals = points
        .map((p) => Number(p[cfg.key]))
        .filter((v) => !isNaN(v) && v !== null);

      if (vals.length > 0) {
        const min = Math.min(...vals);
        const max = Math.max(...vals);
        seriesBounds[cfg.key as string] = { min, max };
        if (min < overallMin) overallMin = min;
        if (max > overallMax) overallMax = max;
      } else {
        seriesBounds[cfg.key as string] = { min: 0, max: 1 };
      }
    });

    if (overallMin === Infinity) overallMin = 0;
    if (overallMax === -Infinity) overallMax = 1;

    return { minSol, maxSol, minVal: overallMin, maxVal: overallMax, seriesBounds };
  }, [points, seriesConfigs]);

  const padding = { top: 20, right: 30, bottom: 35, left: 55 };
  const svgWidth = 800;
  const chartWidth = svgWidth - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  // Coordinate mapping functions
  const getX = useCallback((sol: number) => {
    const solRange = Math.max(1, bounds.maxSol - bounds.minSol);
    return padding.left + ((sol - bounds.minSol) / solRange) * chartWidth;
  }, [bounds.maxSol, bounds.minSol, chartWidth, padding.left]);

  const getY = useCallback((val: number, key: string) => {
    if (normalized) {
      const sBound = bounds.seriesBounds[key] || { min: 0, max: 1 };
      const range = Math.max(0.001, sBound.max - sBound.min);
      const normVal = (val - sBound.min) / range;
      return padding.top + chartHeight - normVal * chartHeight;
    } else {
      const range = Math.max(0.001, bounds.maxVal - bounds.minVal);
      return padding.top + chartHeight - ((val - bounds.minVal) / range) * chartHeight;
    }
  }, [normalized, bounds.seriesBounds, bounds.maxVal, bounds.minVal, chartHeight, padding.top]);

  // Build SVG Paths
  const paths = useMemo(() => {
    return seriesConfigs.map((cfg) => {
      const validPoints = points
        .filter((p) => p[cfg.key] !== null && p[cfg.key] !== undefined && !isNaN(Number(p[cfg.key])))
        .map((p) => ({
          x: getX(p.sol),
          y: getY(Number(p[cfg.key]), cfg.key as string)
        }));

      if (validPoints.length === 0) return { key: cfg.key, d: "", color: cfg.color };

      const d = validPoints.reduce((acc, pt, i) => {
        return i === 0 ? `M ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}` : `${acc} L ${pt.x.toFixed(1)} ${pt.y.toFixed(1)}`;
      }, "");

      return { key: cfg.key, d, color: cfg.color };
    });
  }, [points, seriesConfigs, getX, getY]);

  const highlightPoints = useMemo(() => {
    if (!highlightSols || highlightSols.length === 0) return [];
    const solSet = new Set(highlightSols);
    return points.filter((p) => solSet.has(p.sol));
  }, [points, highlightSols]);

  const handleMouseMove = useCallback((e: React.MouseEvent<SVGSVGElement>) => {
    if (points.length === 0) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const clientX = e.clientX;

    if (rafId.current !== null) {
      cancelAnimationFrame(rafId.current);
    }

    rafId.current = requestAnimationFrame(() => {
      const relX = ((clientX - rect.left) / rect.width) * svgWidth;
      if (relX >= padding.left && relX <= svgWidth - padding.right) {
        const solRange = bounds.maxSol - bounds.minSol;
        const approxSol = bounds.minSol + ((relX - padding.left) / chartWidth) * solRange;
        const closest = findClosestPointIdx(points, approxSol);
        setHoveredIdx((prev) => (prev === closest ? prev : closest));
      }
    });
  }, [points, bounds, padding.left, padding.right, chartWidth, svgWidth]);

  const handleMouseLeave = useCallback(() => {
    if (rafId.current !== null) {
      cancelAnimationFrame(rafId.current);
      rafId.current = null;
    }
    setHoveredIdx(null);
  }, []);

  const hoveredPoint = hoveredIdx !== null ? points[hoveredIdx] : null;

  return (
    <div className="relative w-full bg-mars-panel border border-mars-border rounded-lg p-3 shadow-panel">
      {/* Chart Legend */}
      <div className="flex flex-wrap items-center justify-between gap-3 mb-2 px-1 text-xs">
        <div className="flex items-center gap-4">
          {seriesConfigs.map((cfg) => (
            <div key={cfg.key as string} className="flex items-center gap-1.5 font-mono">
              <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: cfg.color }} />
              <span className="text-slate-300 font-semibold">{cfg.label}</span>
              <span className="text-slate-500">({cfg.unit})</span>
            </div>
          ))}
          {normalized && (
            <span className="text-[11px] px-1.5 py-0.5 rounded bg-mars-surface text-mars-cyan border border-mars-cyan/30">
              Normalized [0–1] View
            </span>
          )}
        </div>

        {hoveredPoint && (
          <div className="flex items-center gap-3 font-mono text-xs text-slate-300 bg-mars-surface px-2.5 py-1 rounded border border-mars-borderBright">
            <span className="text-mars-amber font-bold">Sol {hoveredPoint.sol}</span>
            <span className="text-slate-400">{hoveredPoint.terrestrial_date}</span>
            {seriesConfigs.map((cfg) => (
              <span key={cfg.key as string} style={{ color: cfg.color }}>
                {hoveredPoint[cfg.key] !== null ? `${Number(hoveredPoint[cfg.key]).toFixed(1)} ${cfg.unit}` : "N/A"}
              </span>
            ))}
          </div>
        )}
      </div>

      {/* SVG Canvas */}
      <div className="w-full overflow-hidden">
        <svg
          viewBox={`0 0 ${svgWidth} ${height}`}
          className="w-full h-auto cursor-crosshair select-none"
          onMouseMove={handleMouseMove}
          onMouseLeave={handleMouseLeave}
        >
          {/* Background Grid Lines */}
          {[0, 0.25, 0.5, 0.75, 1].map((pct) => {
            const y = padding.top + pct * chartHeight;
            const val = bounds.maxVal - pct * (bounds.maxVal - bounds.minVal);
            return (
              <g key={pct}>
                <line
                  x1={padding.left}
                  y1={y}
                  x2={svgWidth - padding.right}
                  y2={y}
                  stroke="#1e2e47"
                  strokeDasharray="3 3"
                />
                <text
                  x={padding.left - 8}
                  y={y + 3}
                  textAnchor="end"
                  className="text-[9px] fill-slate-500 font-mono"
                >
                  {normalized ? `${(1 - pct).toFixed(2)}` : `${val.toFixed(0)}`}
                </text>
              </g>
            );
          })}

          {/* Sensor Gap Highlights */}
          {sensorGaps.map((gap, i) => {
            const x1 = Math.max(padding.left, getX(gap.start_sol));
            const x2 = Math.min(svgWidth - padding.right, getX(gap.end_sol));
            if (x2 <= x1) return null;
            return (
              <g key={i}>
                <rect
                  x={x1}
                  y={padding.top}
                  width={x2 - x1}
                  height={chartHeight}
                  fill="#ef4444"
                  fillOpacity="0.08"
                />
                <line x1={x1} y1={padding.top} x2={x1} y2={padding.top + chartHeight} stroke="#ef4444" strokeWidth="1" strokeDasharray="2 2" />
                <line x1={x2} y1={padding.top} x2={x2} y2={padding.top + chartHeight} stroke="#ef4444" strokeWidth="1" strokeDasharray="2 2" />
              </g>
            );
          })}

          {/* X Axis Ticks */}
          {[0, 0.2, 0.4, 0.6, 0.8, 1].map((pct) => {
            const solVal = Math.round(bounds.minSol + pct * (bounds.maxSol - bounds.minSol));
            const x = padding.left + pct * chartWidth;
            return (
              <g key={pct}>
                <line x1={x} y1={padding.top + chartHeight} x2={x} y2={padding.top + chartHeight + 4} stroke="#2d4468" />
                <text
                  x={x}
                  y={padding.top + chartHeight + 16}
                  textAnchor="middle"
                  className="text-[9px] fill-slate-400 font-mono"
                >
                  Sol {solVal}
                </text>
              </g>
            );
          })}

          {/* Line Paths */}
          {paths.map((p) => (
            <path
              key={p.key as string}
              d={p.d}
              fill="none"
              stroke={p.color}
              strokeWidth="1.5"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
          ))}

          {/* Anomaly Highlight Markers */}
          {highlightPoints.map((pt) => {
            const x = getX(pt.sol);
            return (
              <g key={pt.sol}>
                <line x1={x} y1={padding.top} x2={x} y2={padding.top + chartHeight} stroke="#e07a5f" strokeWidth="1.5" strokeDasharray="3 3" />
                <circle cx={x} cy={padding.top + 10} r="4" fill="#e07a5f" />
                <text x={x} y={padding.top - 4} textAnchor="middle" className="text-[9px] fill-mars-amber font-mono font-bold">
                  ANOMALY
                </text>
              </g>
            );
          })}

          {/* Hover Indicator Crosshair */}
          {hoveredPoint && (
            <g>
              <line
                x1={getX(hoveredPoint.sol)}
                y1={padding.top}
                x2={getX(hoveredPoint.sol)}
                y2={padding.top + chartHeight}
                stroke="#38bdf8"
                strokeWidth="1"
                strokeDasharray="2 2"
              />
              {seriesConfigs.map((cfg) => {
                const val = Number(hoveredPoint[cfg.key]);
                if (isNaN(val) || val === null) return null;
                return (
                  <circle
                    key={cfg.key as string}
                    cx={getX(hoveredPoint.sol)}
                    cy={getY(val, cfg.key as string)}
                    r="4"
                    fill={cfg.color}
                    stroke="#04070c"
                    strokeWidth="2"
                  />
                );
              })}
            </g>
          )}
        </svg>
      </div>

      {/* Axis Labels */}
      <div className="flex justify-between items-center px-2 pt-1 text-[10px] text-slate-500 font-mono">
        <span>Gale Crater Observation Time-Series</span>
        <span>Timeline Range: Sol {bounds.minSol} → Sol {bounds.maxSol}</span>
      </div>
    </div>
  );
};
