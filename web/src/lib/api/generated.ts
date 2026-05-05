/**
 * Generated from the FastAPI OpenAPI schema.
 * Refresh with: npm run gen:api-types
 */

export interface DemoScanRequest {
  rows?: number;
  showSafe?: boolean;
  maxDisplay?: number;
}

export interface ScanMeta {
  mode: string;
  filename: string | null;
  rowCount: number;
  returnedRowCount: number;
  processingTimeMs: number;
}

export interface ScanSummary {
  total: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  safe: number;
  anomalyCount: number;
}

export interface ThreatCount {
  name: string;
  count: number;
}

export interface DistributionItem {
  level: string;
  count: number;
}

export interface ResultRow {
  src_ip: string;
  dst_ip: string;
  protocol: string;
  dst_port: number;
  if_anomaly: boolean;
  threats: string[];
  risk_score: number;
  risk_label: string;
}

export interface ScanResponse {
  meta: ScanMeta;
  summary: ScanSummary;
  topThreats: ThreatCount[];
  distribution: DistributionItem[];
  rows: ResultRow[];
  exportToken: string | null;
  warnings: string[];
}

export interface HealthResponse {
  status: string;
  version: string;
}
