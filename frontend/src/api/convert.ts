import { apiPostForm } from "./client";

export interface JobAcceptedResponse {
  job_id: string;
  status: string;
}

/** Upload files to the backend and start a conversion job. */
export function uploadFiles(files: File[]): Promise<JobAcceptedResponse> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  return apiPostForm<JobAcceptedResponse>("/api/convert", formData);
}
