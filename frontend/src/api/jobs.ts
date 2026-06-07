import { apiGet, API_BASE_URL } from "./client";

export interface JobLogItem {
  id: number;
  level: string;
  message: string;
  created_at: string;
}

export interface JobSummary {
  files: number;
  total_rows: number;
  valid_compounds: number;
}

export interface CompoundResultItem {
  id: number;
  source_file: string;
  location: string;
  compound_index: number;
  raw_smiles: string | null;
  canonical_smiles: string | null;
  validation_status: string;
  error: string | null;
  image_url: string | null;
}

export interface JobStatusResponse {
  job_id: string;
  status: string;
  error?: string | null;
  logs: JobLogItem[];
  summary?: JobSummary | null;
  results: CompoundResultItem[];
}

export function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  return apiGet<JobStatusResponse>(`/api/jobs/${jobId}`);
}

/** Absolute URL for a result's cropped image (the API returns a relative path). */
export function absoluteUrl(path: string): string {
  return `${API_BASE_URL}${path}`;
}

/** Direct URL to the CSV for a completed job (used as an <a href> download). */
export function downloadCsvUrl(jobId: string): string {
  return `${API_BASE_URL}/api/jobs/${jobId}/download`;
}

/** Direct URL to the ZIP (CSV + per-compound depiction/crop PNGs) for a completed job. */
export function downloadZipUrl(jobId: string): string {
  return `${API_BASE_URL}/api/jobs/${jobId}/download.zip`;
}
