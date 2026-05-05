import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import type { ScanApiClient } from "@/src/lib/api/client";
import type { ScanResponse } from "@/src/lib/api/generated";
import { ScanWorkbench } from "@/components/scan-workbench";

const mockResponse: ScanResponse = {
  meta: {
    mode: "demo",
    filename: null,
    rowCount: 120,
    returnedRowCount: 40,
    processingTimeMs: 920,
  },
  summary: {
    total: 120,
    critical: 8,
    high: 11,
    medium: 14,
    low: 21,
    safe: 66,
    anomalyCount: 16,
  },
  topThreats: [{ name: "DoS / DDoS Attack", count: 8 }],
  distribution: [
    { level: "CRITICAL", count: 8 },
    { level: "HIGH", count: 11 },
    { level: "MEDIUM", count: 14 },
    { level: "LOW", count: 21 },
    { level: "SAFE", count: 66 },
  ],
  rows: [
    {
      src_ip: "10.0.0.99",
      dst_ip: "192.168.1.2",
      protocol: "TCP",
      dst_port: 80,
      if_anomaly: true,
      threats: ["DoS / DDoS Attack"],
      risk_score: 95,
      risk_label: "CRITICAL",
    },
  ],
  exportToken: "demo-token",
  warnings: [],
};

function buildClient(): ScanApiClient {
  return {
    createDemoScan: vi.fn().mockResolvedValue(mockResponse),
    uploadScan: vi.fn().mockResolvedValue(mockResponse),
  };
}

describe("ScanWorkbench", () => {
  it("runs a demo scan and renders the result summary", async () => {
    const user = userEvent.setup();
    const apiClient = buildClient();

    render(<ScanWorkbench apiBaseUrl="http://localhost:8000" apiClient={apiClient} />);

    await user.click(screen.getByRole("button", { name: /run demo scan/i }));

    await waitFor(() => {
      expect(screen.getByText(/results ready for review/i)).toBeInTheDocument();
    });

    expect(screen.getByText("Critical")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /export csv/i })).toHaveAttribute(
      "href",
      "http://localhost:8000/api/v1/exports/demo-token",
    );
    expect(screen.getByText("10.0.0.99")).toBeInTheDocument();
  });
});
