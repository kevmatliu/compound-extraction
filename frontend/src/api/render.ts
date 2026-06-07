import { API_BASE_URL } from "./client";

/** Render a SMILES to a PNG on the backend. Fallback when the editor's own image
 *  export (ketcher.generateImage) is unavailable. */
export async function renderSmilesPng(smiles: string): Promise<Blob> {
  const res = await fetch(`${API_BASE_URL}/api/render`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ smiles, format: "png" }),
  });
  if (!res.ok) throw new Error(`Render failed (${res.status})`);
  return res.blob();
}
