import React from "react";
import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { ScanApiClient } from "@/src/lib/api/client";
import type { ScanResponse } from "@/src/lib/api/generated";
import { ScanWorkbench } from "@/components/scan-workbench";

afterEach(() => {
  cleanup();
});

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

  it("uploads a selected dataset with numeric scan options", async () => {
    const user = userEvent.setup();
    const apiClient = buildClient();

    render(<ScanWorkbench apiBaseUrl="http://localhost:8000" apiClient={apiClient} />);

    await user.click(screen.getByRole("button", { name: /upload dataset/i }));

    const maxDisplayInput = screen.getByLabelText(/returned rows per response/i);
    await user.clear(maxDisplayInput);
    await user.type(maxDisplayInput, "25");

    const file = new File(
      ["src_port,dst_port,packet_count,byte_count,duration\n1234,80,10,512,1.5\n"],
      "traffic.csv",
      { type: "text/csv" },
    );
    await user.upload(screen.getByLabelText(/dataset file/i), file);
    await user.click(screen.getByRole("button", { name: /upload and scan/i }));

    await waitFor(() => {
      expect(apiClient.uploadScan).toHaveBeenCalledWith("http://localhost:8000", {
        file,
        showSafe: false,
        maxDisplay: 25,
      });
    });
  });

  it("blocks upload scans for files over the browser upload cap", async () => {
    const user = userEvent.setup();
    const apiClient = buildClient();

    render(<ScanWorkbench apiBaseUrl="http://localhost:8000" apiClient={apiClient} />);

    await user.click(screen.getByRole("button", { name: /upload dataset/i }));

    const file = new File(["large"], "large.csv", { type: "text/csv" });
    Object.defineProperty(file, "size", { value: 26 * 1024 * 1024 });

    await user.upload(screen.getByLabelText(/dataset file/i), file);
    await user.click(screen.getByRole("button", { name: /upload and scan/i }));

    expect(screen.getByText(/upload scans are capped at 25 mb/i)).toBeInTheDocument();
    expect(apiClient.uploadScan).not.toHaveBeenCalled();
  });
});
