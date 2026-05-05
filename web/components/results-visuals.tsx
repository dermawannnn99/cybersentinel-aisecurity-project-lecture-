"use client";

import React from "react";

import type { DistributionItem, ScanSummary, ThreatCount } from "@/src/lib/api/generated";

interface ResultsVisualsProps {
  distribution: DistributionItem[];
  topThreats: ThreatCount[];
  summary: ScanSummary;
}

const levelColorMap: Record<string, string> = {
  CRITICAL: "from-alert to-ember",
  HIGH: "from-ember to-orange-300",
  MEDIUM: "from-yellow-400 to-yellow-200",
  LOW: "from-cobalt to-sky-200",
  SAFE: "from-signal to-emerald-200",
};

export function ResultsVisuals({ distribution, topThreats, summary }: ResultsVisualsProps) {
  const maxDistribution = Math.max(...distribution.map((item) => item.count), 1);
  const maxThreats = Math.max(...topThreats.map((item) => item.count), 1);

  return (
    <section className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-5 shadow-panel backdrop-blur">
        <div className="flex items-center justify-between gap-4">
          <div>
            <p className="text-xs uppercase tracking-[0.22em] text-cobalt">Threat Distribution</p>
            <h3 className="mt-2 text-xl font-semibold text-white">Risk levels across the scan</h3>
          </div>
          <p className="font-mono text-sm text-mist/70">{summary.total} total rows</p>
        </div>

        <div className="mt-6 grid gap-4">
          {distribution.map((item) => {
            const width = `${Math.max((item.count / maxDistribution) * 100, item.count > 0 ? 8 : 0)}%`;
            return (
              <div key={item.level} className="grid gap-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-white">{item.level}</span>
                  <span className="font-mono text-mist/70">{item.count}</span>
                </div>
                <div className="h-3 rounded-full bg-white/10">
                  <div
                    className={`h-3 rounded-full bg-gradient-to-r ${levelColorMap[item.level] ?? "from-cobalt to-signal"}`}
                    style={{ width }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="rounded-[28px] border border-white/10 bg-black/20 p-5 shadow-panel backdrop-blur">
        <p className="text-xs uppercase tracking-[0.22em] text-signal">Top Threats</p>
        <h3 className="mt-2 text-xl font-semibold text-white">Rule hits that matter most</h3>
        <div className="mt-6 grid gap-3">
          {topThreats.length === 0 ? (
            <p className="rounded-2xl border border-dashed border-white/10 px-4 py-5 text-sm text-mist/70">
              No rule-based signatures fired in this run.
            </p>
          ) : null}

          {topThreats.map((item) => {
            const width = `${Math.max((item.count / maxThreats) * 100, 10)}%`;
            return (
              <div key={item.name} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-center justify-between gap-4">
                  <p className="text-sm font-medium text-white">{item.name}</p>
                  <span className="font-mono text-sm text-mist/70">{item.count}</span>
                </div>
                <div className="mt-3 h-2 rounded-full bg-white/10">
                  <div
                    className="h-2 rounded-full bg-gradient-to-r from-signal to-cobalt"
                    style={{ width }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
