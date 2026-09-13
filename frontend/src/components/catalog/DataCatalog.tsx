import React, { useState, useEffect } from "react";
import { Database, ExternalLink, ShieldCheck, FileCheck, Layers, BookOpen } from "lucide-react";
import { DataCatalogItem } from "../../lib/types";
import { api } from "../../lib/api";

export const DataCatalog: React.FC = () => {
  const [catalog, setCatalog] = useState<Record<string, DataCatalogItem>>({});
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    let isMounted = true;
    api.getCatalog()
      .then((res) => {
        if (isMounted) {
          setCatalog(res.datasets);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load catalog:", err);
        setLoading(false);
      });
    return () => { isMounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="p-8 text-center font-mono text-xs text-slate-400">
        Loading NASA Planetary Data Catalog & Provenance Registry...
      </div>
    );
  }

  const datasetList = Object.values(catalog);

  return (
    <div className="space-y-6">
      {/* Module Banner */}
      <div className="bg-mars-panel border border-mars-border rounded-lg p-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="text-xs font-mono text-mars-cyan">MODULE 09</div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Database className="w-5 h-5 text-mars-cyan" />
            NASA PLANETARY DATA CATALOG & PROVENANCE REGISTRY
          </h2>
          <p className="text-xs text-slate-400">
            Authoritative source metadata, PDS collection URNs, calibration levels, and physical measurement constraints.
          </p>
        </div>

        <div className="flex items-center gap-2 font-mono text-xs text-slate-400">
          <span>Total Integrated Collections: <strong className="text-white">{datasetList.length}</strong></span>
        </div>
      </div>

      {/* Dataset Cards List */}
      <div className="space-y-6">
        {datasetList.map((ds) => (
          <div
            key={ds.id}
            className="bg-mars-panel border border-mars-border rounded-xl p-6 space-y-4 shadow-panel font-mono text-xs"
          >
            {/* Title & PDS Link */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-mars-border pb-3">
              <div>
                <span className="text-[10px] text-mars-cyan uppercase tracking-wider">{ds.mission}</span>
                <h3 className="text-base font-bold text-white font-sans mt-0.5">{ds.name}</h3>
              </div>
              <div className="flex items-center gap-3">
                <a
                  href={ds.pds_archive_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-3 py-1.5 rounded bg-mars-surface hover:bg-mars-border border border-mars-border text-mars-amber font-bold flex items-center gap-1.5 transition-colors"
                >
                  <span>PDS Archive</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>

            {/* Core Metadata Badges */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-500 text-[10px] block">PDS DATASET ID</span>
                <span className="text-slate-200 font-bold">{ds.dataset_id}</span>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-500 text-[10px] block">DOI REFERENCE</span>
                <span className="text-mars-cyan">{ds.doi}</span>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-500 text-[10px] block">PROCESSING LEVEL</span>
                <span className="text-slate-200 font-bold">{ds.processing_level}</span>
              </div>
              <div className="p-2.5 bg-mars-surface rounded border border-mars-border">
                <span className="text-slate-500 text-[10px] block">DATA COMPLETENESS</span>
                <span className="text-emerald-400 font-bold">{ds.data_quality.completeness_pct}% Completeness</span>
              </div>
            </div>

            {/* Spatial & Temporal Coverage */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-300">
              <div className="p-3 bg-mars-surface/70 rounded border border-mars-border space-y-1">
                <span className="text-slate-400 text-[10px] font-bold block">SPATIAL BOUNDS</span>
                <div>Site: {ds.spatial_coverage.site}</div>
                <div className="text-[11px] text-slate-400">
                  Lat: {ds.spatial_coverage.latitude_deg} | Lon: {ds.spatial_coverage.longitude_deg_east} | Elevation: {ds.spatial_coverage.elevation_km} km
                </div>
              </div>

              <div className="p-3 bg-mars-surface/70 rounded border border-mars-border space-y-1">
                <span className="text-slate-400 text-[10px] font-bold block">TEMPORAL COVERAGE</span>
                <div>{ds.temporal_coverage.start_earth_date} to {ds.temporal_coverage.end_earth_date}</div>
                <div className="text-[11px] text-slate-400">
                  Sols: {ds.temporal_coverage.start_sol} → {ds.temporal_coverage.end_sol} ({ds.temporal_coverage.observation_cadence})
                </div>
              </div>
            </div>

            {/* Variables Schema Table */}
            <div className="space-y-2">
              <span className="text-slate-400 text-[10px] font-bold block uppercase">
                CALIBRATED SCIENTIFIC VARIABLES ({ds.variables.length})
              </span>
              <div className="overflow-x-auto">
                <table className="w-full text-left text-[11px]">
                  <thead className="bg-mars-surface text-slate-400 border-b border-mars-border uppercase text-[9px]">
                    <tr>
                      <th className="py-2 px-2.5">Variable</th>
                      <th className="py-2 px-2.5">Unit</th>
                      <th className="py-2 px-2.5">Physical Range</th>
                      <th className="py-2 px-2.5">Uncertainty</th>
                      <th className="py-2 px-2.5">Sensor Hardware</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-mars-border/30 text-slate-300">
                    {ds.variables.map((v) => (
                      <tr key={v.id}>
                        <td className="py-1.5 px-2.5 font-bold text-white">{v.name}</td>
                        <td className="py-1.5 px-2.5 text-mars-cyan">{v.unit}</td>
                        <td className="py-1.5 px-2.5 text-slate-400">
                          {v.physical_range ? `[${v.physical_range[0]}, ${v.physical_range[1]}]` : "--"}
                        </td>
                        <td className="py-1.5 px-2.5 text-mars-amber">{v.uncertainty}</td>
                        <td className="py-1.5 px-2.5 text-slate-400">{v.sensor}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Known Limitations */}
            <div className="p-3 bg-mars-surface/40 rounded border border-mars-border text-[11px] space-y-1 font-sans">
              <span className="font-mono text-rose-400 font-bold block text-[10px]">DOCUMENTED SENSOR LIMITATIONS:</span>
              <ul className="list-disc list-inside text-slate-400 space-y-0.5">
                {ds.data_quality.known_limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
