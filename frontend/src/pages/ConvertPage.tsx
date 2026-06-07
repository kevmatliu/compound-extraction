import { useEffect, useRef, useState } from "react";
import { uploadFiles } from "../api/convert";
import {
  downloadCsvUrl,
  downloadZipUrl,
  getJobStatus,
  type CompoundResultItem,
  type JobSummary,
} from "../api/jobs";
import { renderSmilesPng } from "../api/render";
import { CompoundCard } from "../components/CompoundCard";
import { Dropzone } from "../components/Dropzone";
import { KetcherEditor, type KetcherEditorHandle } from "../components/KetcherEditor";

const TERMINAL = new Set(["completed", "failed"]);

function triggerDownload(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export function ConvertPage() {
  const [files, setFiles] = useState<File[]>([]);
  const [jobId, setJobId] = useState<string | null>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [progress, setProgress] = useState<string>("");
  const [summary, setSummary] = useState<JobSummary | null>(null);
  const [results, setResults] = useState<CompoundResultItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editorSmiles, setEditorSmiles] = useState<string>("");

  const ketcherRef = useRef<KetcherEditorHandle | null>(null);
  const busy = Boolean(jobId) && !TERMINAL.has(status ?? "");

  // Poll the job until it reaches a terminal state.
  useEffect(() => {
    if (!jobId) return;
    let cancelled = false;
    let timeoutId: number | null = null;

    const poll = async () => {
      try {
        const response = await getJobStatus(jobId);
        if (cancelled) return;
        setStatus(response.status);
        setSummary(response.summary ?? null);
        setResults(response.results);
        const last = response.logs[response.logs.length - 1];
        if (last) setProgress(last.message);
        if (response.status === "failed") {
          setError(response.error ?? "Conversion failed.");
        }
        if (TERMINAL.has(response.status)) return;
        timeoutId = window.setTimeout(() => void poll(), 250);
      } catch (pollError) {
        if (cancelled) return;
        setError(pollError instanceof Error ? pollError.message : String(pollError));
      }
    };

    void poll();
    return () => {
      cancelled = true;
      if (timeoutId !== null) window.clearTimeout(timeoutId);
    };
  }, [jobId]);

  const handleConvert = async () => {
    if (files.length === 0) return;
    setError(null);
    setSummary(null);
    setResults([]);
    setProgress("Uploading…");
    setStatus("pending");
    try {
      const response = await uploadFiles(files);
      setJobId(response.job_id);
      setStatus(response.status);
    } catch (submitError) {
      setStatus(null);
      setError(submitError instanceof Error ? submitError.message : String(submitError));
    }
  };

  const reset = () => {
    setFiles([]);
    setJobId(null);
    setStatus(null);
    setProgress("");
    setSummary(null);
    setResults([]);
    setError(null);
  };

  // Load a result's SMILES into the editor on the right.
  const handleLoadToEditor = (smiles: string) => {
    setEditorSmiles(smiles);
    void ketcherRef.current?.setSmiles(smiles);
  };

  // Export the editor's current drawing as a PNG (falls back to backend render).
  const handleExportPng = async () => {
    let blob = await ketcherRef.current?.getImageBlob("png");
    if (!blob) {
      const smiles = (await ketcherRef.current?.getSmiles())?.trim();
      if (smiles) {
        try {
          blob = await renderSmilesPng(smiles);
        } catch (e) {
          setError(e instanceof Error ? e.message : String(e));
          return;
        }
      }
    }
    if (blob) triggerDownload(blob, "structure.png");
  };

  const isComplete = status === "completed";

  return (
    <main className="workspace">
      <div className="workspace-left">
        <header className="page-header">
          <h1>Compound Extraction</h1>
          <p>
            Upload images, PDFs, or slide decks. Each chemical structure is detected,
            recognized into SMILES, standardized, and exported. Send any result to the
            editor on the right.
          </p>
        </header>

        <section className="upload-card">
          <Dropzone files={files} onChange={setFiles} disabled={busy} />
          <div className="upload-actions">
            <button className="btn-primary" onClick={handleConvert} disabled={busy || files.length === 0}>
              {busy ? "Processing…" : "Convert"}
            </button>
            {(files.length > 0 || jobId) && !busy && (
              <button className="btn-ghost" onClick={reset}>
                Clear
              </button>
            )}
          </div>
          {error && <p className="alert">{error}</p>}
        </section>

        {busy && (
          <section className="progress">
            <span className="spinner" aria-hidden />
            <span>{progress || "Working…"}</span>
          </section>
        )}

        {isComplete && (
          <section className="results">
            <div className="results-header">
              <div>
                <h2>Results</h2>
                {summary && (
                  <p className="muted">
                    {summary.valid_compounds} valid · {summary.total_rows} total · {summary.files} file(s)
                  </p>
                )}
              </div>
              <div className="results-downloads">
                <a className="btn-ghost" href={jobId ? downloadCsvUrl(jobId) : undefined} download="compounds.csv">
                  Download CSV
                </a>
                <a className="btn-primary" href={jobId ? downloadZipUrl(jobId) : undefined} download="compounds.zip">
                  Download ZIP
                </a>
              </div>
            </div>

            {results.length === 0 ? (
              <p className="muted">No structures were detected.</p>
            ) : (
              <div className="compound-grid">
                {results.map((item) => (
                  <CompoundCard key={item.id} item={item} onLoadToEditor={handleLoadToEditor} />
                ))}
              </div>
            )}
          </section>
        )}
      </div>

      <aside className="workspace-right">
        <div className="editor-panel">
          <div className="editor-toolbar">
            <span className="editor-title">Editor</span>
            <span className="editor-actions">
              <button className="btn-ghost" onClick={() => void ketcherRef.current?.clear()}>
                Clear
              </button>
              <button className="btn-primary" onClick={handleExportPng}>
                Export PNG
              </button>
            </span>
          </div>
          <KetcherEditor ref={ketcherRef} value={editorSmiles} height={560} />
        </div>
      </aside>
    </main>
  );
}
