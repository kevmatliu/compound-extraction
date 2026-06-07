import { useState } from "react";
import { absoluteUrl, type CompoundResultItem } from "../api/jobs";

interface CompoundCardProps {
  item: CompoundResultItem;
}

// Human-readable label + visual tone for each backend validation status.
const STATUS_META: Record<string, { label: string; tone: string }> = {
  valid: { label: "Valid", tone: "ok" },
  parse_failed: { label: "Parse failed", tone: "danger" },
  sanitize_failed: { label: "Sanitize failed", tone: "danger" },
  standardize_failed: { label: "Standardize failed", tone: "danger" },
  unprocessed: { label: "Skipped", tone: "neutral" },
};

export function CompoundCard({ item }: CompoundCardProps) {
  const [copied, setCopied] = useState(false);
  const smiles = item.canonical_smiles ?? item.raw_smiles;
  const status = STATUS_META[item.validation_status] ?? {
    label: item.validation_status,
    tone: "neutral",
  };

  const copy = async () => {
    if (!smiles) return;
    await navigator.clipboard.writeText(smiles);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1200);
  };

  return (
    <article className="compound-card">
      <div className="compound-image">
        {item.image_url ? (
          <img src={absoluteUrl(item.image_url)} alt={`Structure from ${item.source_file}`} />
        ) : (
          <span className="compound-image-empty">No image</span>
        )}
      </div>

      <div className="compound-body">
        <div className="compound-meta">
          <span className={`badge badge-${status.tone}`}>{status.label}</span>
          <span className="compound-location">{item.location}</span>
        </div>

        {smiles ? (
          <div className="smiles-row">
            <code className="smiles-text">{smiles}</code>
            <button type="button" className="copy-btn" onClick={copy}>
              {copied ? "Copied" : "Copy"}
            </button>
          </div>
        ) : (
          <p className="compound-error">{item.error ?? "No SMILES produced"}</p>
        )}

        <p className="compound-source" title={item.source_file}>
          {item.source_file}
        </p>
      </div>
    </article>
  );
}
