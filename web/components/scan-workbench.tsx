"use client";

import dynamic from "next/dynamic";
import React, { startTransition, useDeferredValue, useState, useTransition } from "react";

import type { DemoScanRequest, ResultRow, ScanResponse } from "@/src/lib/api/generated";
import { defaultScanApiClient, type ScanApiClient } from "@/src/lib/api/client";

const ResultsVisuals = dynamic(
  () => import("@/components/results-visuals").then((module) => module.ResultsVisuals),
  {
    ssr: false,
    loading: () => (
      <div className="rounded-[28px] border border-white/10 bg-white/5 p-6 text-sm text-mist/70">
        Loading charts...
      </div>
    ),
  },
);

interface ScanWorkbenchProps {
  apiBaseUrl: string;
  apiClient?: ScanApiClient;
}

const levelOptions = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW", "SAFE"] as const;

function buildSearchableText(row: ResultRow): string {
  return [row.src_ip, row.dst_ip, row.protocol, row.risk_label, row.threats.join(" ")]
    .join(" ")
    .toLowerCase();
}

function getStatusTone(label: string): string {
  if (label === "CRITICAL") return "text-alert";
  if (label === "HIGH") return "text-ember";
  if (label === "MEDIUM") return "text-yellow-300";
  if (label === "LOW") return "text-cobalt";
  return "text-signal";
}

export function ScanWorkbench({
  apiBaseUrl,
  apiClient = defaultScanApiClient,
}: ScanWorkbenchProps) {
  const [mode, setMode] = useState<"demo" | "upload">("demo");
  const [rows, setRows] = useState(300);
  const [showSafe, setShowSafe] = useState(false);
  const [maxDisplay, setMaxDisplay] = useState(50);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [response, setResponse] = useState<ScanResponse | null>(null);
  const [query, setQuery] = useState("");
  const [level, setLevel] = useState<(typeof levelOptions)[number]>("ALL");
  const [isPending, beginTransition] = useTransition();

  const deferredQuery = useDeferredValue(query);
  const deferredLevel = useDeferredValue(level);

  const filteredRows = response
    ? response.rows.filter((row) => {
        const normalizedQuery = deferredQuery.trim().toLowerCase();

        if (deferredLevel !== "ALL" && row.risk_label !== deferredLevel) {
          return false;
        }

        if (!normalizedQuery) {
          return true;
        }

        return buildSearchableText(row).includes(normalizedQuery);
      })
    : [];

  const summaryCards = response
    ? [
        { label: "Critical", value: response.summary.critical, tone: "text-alert" },
        { label: "High", value: response.summary.high, tone: "text-ember" },
        { label: "Medium", value: response.summary.medium, tone: "text-yellow-300" },
        { label: "Low", value: response.summary.low, tone: "text-cobalt" },
        { label: "Safe", value: response.summary.safe, tone: "text-signal" },
        { label: "ML anomalies", value: response.summary.anomalyCount, tone: "text-white" },
      ]
    : [];

  async function submitDemoScan(payload: DemoScanRequest) {
    const nextResponse = await apiClient.createDemoScan(apiBaseUrl, payload);
    setResponse(nextResponse);
  }

  async function submitUploadScan(file: File) {
    const nextResponse = await apiClient.uploadScan(apiBaseUrl, {
      file,
      showSafe,
      maxDisplay,
    });
    setResponse(nextResponse);
  }

  function handleQueryChange(value: string) {
    startTransition(() => {
      setQuery(value);
    });
  }

  function handleLevelChange(value: (typeof levelOptions)[number]) {
    startTransition(() => {
      setLevel(value);
    });
  }

  async function handleRunScan() {
    setErrorMessage(null);

    beginTransition(async () => {
      try {
        if (mode === "demo") {
          await submitDemoScan({ rows, showSafe, maxDisplay });
          return;
        }

        if (!selectedFile) {
          setErrorMessage("Select a dataset file before running an upload scan.");
          return;
        }

        await submitUploadScan(selectedFile);
      } catch (error) {
        setResponse(null);
        setErrorMessage(error instanceof Error ? error.message : "Unexpected scan error.");
      }
    });
  }

  return (
    <section className="grid gap-6">
      <div className="grid gap-6 xl:grid-cols-[360px_1fr]">
        <aside className="rounded-[32px] border border-white/10 bg-black/25 p-6 shadow-panel backdrop-blur">
          <div className="space-y-3">
            <p className="text-xs uppercase tracking-[0.22em] text-signal">Mission Control</p>
            <h2 className="text-2xl font-semibold text-white">Run an analyst scan</h2>
            <p className="text-sm leading-6 text-mist/70">
              Use demo mode for a fast walkthrough or upload a supported dataset for a live threat
              pass.
            </p>
          </div>

          <div className="mt-6 grid grid-cols-2 gap-3 rounded-3xl border border-white/10 bg-white/5 p-2">
            <button
              className={`rounded-2xl px-4 py-3 text-sm transition ${
                mode === "demo" ? "bg-signal text-ink" : "bg-transparent text-mist/75 hover:bg-white/5"
              }`}
              onClick={() => setMode("demo")}
              type="button"
            >
              Demo Scan
            </button>
            <button
              className={`rounded-2xl px-4 py-3 text-sm transition ${
                mode === "upload" ? "bg-cobalt text-ink" : "bg-transparent text-mist/75 hover:bg-white/5"
              }`}
              onClick={() => setMode("upload")}
              type="button"
            >
              Upload Dataset
            </button>
          </div>

          <div className="mt-6 grid gap-5">
            <label className="grid gap-2">
              <span className="text-sm text-mist/80">Returned rows per response</span>
              <input
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none ring-0 transition placeholder:text-mist/30 focus:border-signal"
                min={10}
                max={500}
                onChange={(event) => {
                  const next = Number(event.target.value);
                  if (!Number.isNaN(next)) setMaxDisplay(next);
                }}
                type="number"
                value={maxDisplay}
              />
            </label>

            <label className="flex items-center gap-3 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-mist/80">
              <input
                checked={showSafe}
                className="h-4 w-4 accent-signal"
                onChange={(event) => setShowSafe(event.target.checked)}
                type="checkbox"
              />
              Include SAFE traffic in returned rows
            </label>

            {mode === "demo" ? (
              <label className="grid gap-2">
                <span className="text-sm text-mist/80">Demo row count</span>
                <input
                  className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-white outline-none transition focus:border-signal"
                  max={5000}
                  min={50}
onChange={(event) => {
                  const next = Number(event.target.value);
                  if (!Number.isNaN(next)) setRows(next);
                }}
                type="number"
                value={rows}
                />
              </label>
            ) : (
              <label className="grid gap-2">
                <span className="text-sm text-mist/80">Dataset file</span>
                <input
                  accept=".csv,.txt"
                  className="rounded-2xl border border-dashed border-white/15 bg-white/5 px-4 py-3 text-sm text-mist/80 file:mr-4 file:rounded-full file:border-0 file:bg-white/10 file:px-3 file:py-2 file:text-sm file:text-white"
                  onChange={(event) => setSelectedFile(event.target.files?.[0] ?? null)}
                  type="file"
                />
                <span className="text-xs text-mist/50">
                  Interactive uploads are capped at 25 MB for browser-first scans.
                </span>
              </label>
            )}
          </div>

          <button
            className="mt-8 inline-flex w-full items-center justify-center rounded-2xl bg-white px-4 py-3 text-sm font-medium text-ink transition hover:bg-signal disabled:cursor-not-allowed disabled:bg-white/20 disabled:text-mist/50"
            disabled={isPending}
            onClick={handleRunScan}
            type="button"
          >
            {isPending ? "Running scan..." : mode === "demo" ? "Run demo scan" : "Upload and scan"}
          </button>

          {errorMessage ? (
            <div className="mt-4 rounded-2xl border border-alert/30 bg-alert/10 px-4 py-3 text-sm text-red-100">
              {errorMessage}
            </div>
          ) : null}
        </aside>

        <div className="grid gap-6">
          <div className="rounded-[32px] border border-white/10 bg-white/5 p-6 shadow-panel backdrop-blur">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div>
                <p className="text-xs uppercase tracking-[0.22em] text-cobalt">Scan Status</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">
                  {response ? "Results ready for review" : "Waiting for the next scan"}
                </h2>
              </div>
              <div className="flex flex-wrap gap-3 text-sm text-mist/70">
                <span className="rounded-full border border-white/10 bg-black/20 px-3 py-2 font-mono">
                  API: {apiBaseUrl}
                </span>
                {response?.exportToken ? (
                  <a
                    className="rounded-full border border-signal/30 bg-signal/10 px-3 py-2 font-medium text-signal transition hover:bg-signal/20"
                    href={`${apiBaseUrl}/api/v1/exports/${response.exportToken}`}
                  >
                    Export CSV
                  </a>
                ) : null}
              </div>
            </div>

            {response ? (
              <div className="mt-6 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {summaryCards.map((card) => (
                  <div
                    key={card.label}
                    className="rounded-3xl border border-white/10 bg-black/20 px-5 py-4"
                  >
                    <p className="text-sm text-mist/70">{card.label}</p>
                    <p className={`mt-2 text-3xl font-semibold ${card.tone}`}>{card.value}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="mt-6 rounded-[28px] border border-dashed border-white/10 bg-black/15 p-8 text-sm leading-7 text-mist/65">
                The first render stays idle on purpose. No request is sent until you explicitly run a
                scan, which keeps the initial page load clean and avoids startup waterfalls.
              </div>
            )}
          </div>

          {response ? (
            <ResultsVisuals
              distribution={response.distribution}
              summary={response.summary}
              topThreats={response.topThreats}
            />
          ) : null}
        </div>
      </div>

      {response ? (
        <section className="rounded-[32px] border border-white/10 bg-black/25 p-6 shadow-panel backdrop-blur">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <p className="text-xs uppercase tracking-[0.22em] text-signal">Analyst Table</p>
              <h3 className="mt-2 text-2xl font-semibold text-white">Review returned traffic rows</h3>
            </div>

            <div className="grid gap-3 md:grid-cols-[minmax(220px,1fr)_180px]">
              <input
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none placeholder:text-mist/35 focus:border-signal"
                onChange={(event) => handleQueryChange(event.target.value)}
                placeholder="Search IP, protocol, threat, or level"
                type="search"
                value={query}
              />

              <select
                className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-white outline-none focus:border-signal"
                onChange={(event) => handleLevelChange(event.target.value as (typeof levelOptions)[number])}
                value={level}
              >
                {levelOptions.map((option) => (
                  <option key={option} value={option}>
                    {option}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {response.warnings.length > 0 ? (
            <div className="mt-5 grid gap-2">
              {response.warnings.map((warning) => (
                <div
                  key={warning}
                  className="rounded-2xl border border-yellow-300/20 bg-yellow-300/10 px-4 py-3 text-sm text-yellow-100"
                >
                  {warning}
                </div>
              ))}
            </div>
          ) : null}

          <div className="mt-6 overflow-hidden rounded-[28px] border border-white/10">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-white/10">
                <thead className="bg-white/5">
                  <tr className="text-left text-xs uppercase tracking-[0.18em] text-mist/60">
                    <th className="px-4 py-4">Score</th>
                    <th className="px-4 py-4">Level</th>
                    <th className="px-4 py-4">Source</th>
                    <th className="px-4 py-4">Destination</th>
                    <th className="px-4 py-4">Protocol</th>
                    <th className="px-4 py-4">Port</th>
                    <th className="px-4 py-4">ML</th>
                    <th className="px-4 py-4">Threats</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-white/10 bg-black/20 font-mono text-sm text-mist/80">
                  {filteredRows.length === 0 ? (
                    <tr>
                      <td className="px-4 py-8 text-center text-mist/50" colSpan={8}>
                        No returned rows match the current filters.
                      </td>
                    </tr>
                  ) : null}

                  {filteredRows.map((row, index) => (
                    <tr key={`${row.src_ip}-${row.dst_ip}-${row.dst_port}-${index}`} className="align-top">
                      <td className="px-4 py-4 text-white">{row.risk_score}/100</td>
                      <td className={`px-4 py-4 font-semibold ${getStatusTone(row.risk_label)}`}>
                        {row.risk_label}
                      </td>
                      <td className="px-4 py-4">{row.src_ip}</td>
                      <td className="px-4 py-4">{row.dst_ip}</td>
                      <td className="px-4 py-4">{row.protocol}</td>
                      <td className="px-4 py-4">{row.dst_port}</td>
                      <td className="px-4 py-4">
                        {row.if_anomaly ? (
                          <span className="rounded-full bg-alert/15 px-2 py-1 text-xs text-red-100">
                            anomaly
                          </span>
                        ) : (
                          <span className="rounded-full bg-signal/10 px-2 py-1 text-xs text-signal">
                            normal
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-4">
                        {row.threats.length > 0 ? row.threats.join(", ") : "None"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      ) : null}
    </section>
  );
}
