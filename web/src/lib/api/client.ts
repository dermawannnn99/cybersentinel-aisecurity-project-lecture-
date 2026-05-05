import type { DemoScanRequest, ScanResponse } from "@/src/lib/api/generated";

export interface ScanApiClient {
  createDemoScan: (apiBaseUrl: string, payload: DemoScanRequest) => Promise<ScanResponse>;
  uploadScan: (
    apiBaseUrl: string,
    payload: { file: File; showSafe: boolean; maxDisplay: number },
  ) => Promise<ScanResponse>;
}

async function requestJson<T>(input: string, init?: RequestInit): Promise<T> {
  const response = await fetch(input, init);

  if (!response.ok) {
    const fallbackMessage = `Request failed with status ${response.status}`;
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? fallbackMessage);
  }

  return (await response.json()) as T;
}

export const defaultScanApiClient: ScanApiClient = {
  async createDemoScan(apiBaseUrl, payload) {
    return requestJson<ScanResponse>(`${apiBaseUrl}/api/v1/scans/demo`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  },

  async uploadScan(apiBaseUrl, payload) {
    const formData = new FormData();
    formData.set("file", payload.file);
    formData.set("showSafe", String(payload.showSafe));
    formData.set("maxDisplay", String(payload.maxDisplay));

    return requestJson<ScanResponse>(`${apiBaseUrl}/api/v1/scans/upload`, {
      method: "POST",
      body: formData,
    });
  },
};
