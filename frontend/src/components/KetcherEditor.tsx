import { forwardRef, useImperativeHandle, useRef, useState, useEffect, useMemo } from "react";
import { Editor } from "ketcher-react";
// @ts-ignore
import { StandaloneStructServiceProvider } from "ketcher-standalone";
import "ketcher-react/dist/index.css";

export interface KetcherEditorHandle {
  getSmiles: () => Promise<string>;
  setSmiles: (smiles: string) => Promise<string>;
  clear: () => Promise<void>;
  // Render the current drawing to an image Blob (preserves layout). Returns null on
  // failure so the caller can fall back to the backend SMILES renderer.
  getImageBlob: (format?: "png" | "svg") => Promise<Blob | null>;
}

interface KetcherEditorProps {
  value: string;
  height?: number | string;
}

export const KetcherEditor = forwardRef<KetcherEditorHandle, KetcherEditorProps>(function KetcherEditor(
  { value, height = 560 },
  ref
) {
  const structServiceProvider = useMemo(() => new StandaloneStructServiceProvider(), []);
  const [ketcherInstance, setKetcherInstance] = useState<any>(null);
  const lastAppliedSmilesRef = useRef("");
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
      if ((window as any).ketcher === ketcherInstance) {
        (window as any).ketcher = null;
      }
    };
  }, [ketcherInstance]);

  useImperativeHandle(
    ref,
    () => ({
      async getSmiles() {
        if (!ketcherInstance) return "";
        try {
          return await ketcherInstance.getSmiles();
        } catch (e) {
          console.error("Ketcher getSmiles error", e);
          return "";
        }
      },
      async setSmiles(smiles: string) {
        const nextSmiles = smiles.trim();
        if (!ketcherInstance) return "";
        try {
          await ketcherInstance.setMolecule(nextSmiles);
          lastAppliedSmilesRef.current = nextSmiles;
          return nextSmiles;
        } catch (e) {
          console.error("Ketcher setMolecule error", e);
          return "";
        }
      },
      async clear() {
        if (!ketcherInstance) return;
        try {
          await ketcherInstance.setMolecule("");
          lastAppliedSmilesRef.current = "";
        } catch (e) {
          console.error("Ketcher clear error", e);
        }
      },
      async getImageBlob(format: "png" | "svg" = "png") {
        if (!ketcherInstance) return null;
        try {
          const molString = await ketcherInstance.getMolfile();
          const result = await ketcherInstance.generateImage(molString, {
            outputFormat: format,
            backgroundColor: "FFFFFF",
          });
          return result instanceof Blob ? result : new Blob([result], { type: `image/${format}` });
        } catch (e) {
          console.error("Ketcher generateImage error", e);
          return null;
        }
      },
    }),
    [ketcherInstance]
  );

  // Apply externally-provided SMILES into the canvas when it changes.
  useEffect(() => {
    const nextSmiles = value.trim();
    if (!ketcherInstance || nextSmiles === lastAppliedSmilesRef.current) {
      return;
    }
    void (async () => {
      try {
        await ketcherInstance.setMolecule(nextSmiles);
        if (isMountedRef.current) {
          lastAppliedSmilesRef.current = nextSmiles;
        }
      } catch (error) {
        if (isMountedRef.current) {
          console.error("Failed to load SMILES into Ketcher", error);
        }
      }
    })();
  }, [value, ketcherInstance]);

  return (
    <div className="ketcher-frame-wrap" style={{ height, position: "relative" }}>
      <Editor
        staticResourcesUrl={import.meta.env.BASE_URL}
        structServiceProvider={structServiceProvider}
        errorHandler={(message: string) => console.error(message)}
        onInit={(ketcher: any) => {
          setKetcherInstance(ketcher);
          (window as any).ketcher = ketcher;
        }}
      />
    </div>
  );
});
