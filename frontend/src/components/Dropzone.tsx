import { useRef, useState } from "react";

interface DropzoneProps {
  files: File[];
  onChange: (files: File[]) => void;
  disabled?: boolean;
}

const ACCEPT = ".pdf,.png,.jpg,.jpeg,.pptx";
const ACCEPTED_EXT = ["pdf", "png", "jpg", "jpeg", "pptx"];

function isAccepted(file: File): boolean {
  const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
  return ACCEPTED_EXT.includes(ext);
}

/** Drag-and-drop file picker that also supports click-to-browse. */
export function Dropzone({ files, onChange, disabled }: DropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = useState(false);

  // Merge new files, de-duplicating by name+size so re-dropping is idempotent.
  const addFiles = (incoming: File[]) => {
    const accepted = incoming.filter(isAccepted);
    const seen = new Set(files.map((f) => `${f.name}:${f.size}`));
    const merged = [...files];
    for (const file of accepted) {
      const key = `${file.name}:${file.size}`;
      if (!seen.has(key)) {
        seen.add(key);
        merged.push(file);
      }
    }
    onChange(merged);
  };

  const removeFile = (index: number) => {
    onChange(files.filter((_, i) => i !== index));
  };

  return (
    <div>
      <div
        className={`dropzone${dragging ? " is-dragging" : ""}${disabled ? " is-disabled" : ""}`}
        role="button"
        tabIndex={0}
        onClick={() => !disabled && inputRef.current?.click()}
        onKeyDown={(e) => {
          if (!disabled && (e.key === "Enter" || e.key === " ")) inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!disabled) addFiles(Array.from(e.dataTransfer.files));
        }}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept={ACCEPT}
          hidden
          onChange={(e) => {
            addFiles(Array.from(e.target.files ?? []));
            e.target.value = ""; // allow re-selecting the same file
          }}
        />
        <div className="dropzone-icon" aria-hidden>
          ⬆
        </div>
        <p className="dropzone-title">Drag &amp; drop files here</p>
        <p className="dropzone-hint">or click to browse · PNG, JPG, PDF, PPTX</p>
      </div>

      {files.length > 0 && (
        <ul className="file-chips">
          {files.map((file, index) => (
            <li className="file-chip" key={`${file.name}:${file.size}`}>
              <span className="file-chip-name" title={file.name}>
                {file.name}
              </span>
              {!disabled && (
                <button
                  type="button"
                  className="file-chip-remove"
                  aria-label={`Remove ${file.name}`}
                  onClick={() => removeFile(index)}
                >
                  ×
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
