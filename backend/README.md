---
title: Compound Extraction API
emoji: 🧪
colorFrom: green
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# Compound Extraction API

FastAPI backend that extracts chemical structures from uploaded PNG/JPG/PDF/PPTX
files, recognizes them into SMILES with MolScribe, standardizes them with RDKit,
and returns per-compound results plus a downloadable CSV.

The YAML front matter above configures the Hugging Face Space: `sdk: docker` builds
the `Dockerfile`, and `app_port: 7860` is the port the container serves on.

## Endpoints
- `POST /api/convert` — upload files, returns a `job_id`
- `GET /api/jobs/{job_id}` — status, logs, summary, per-compound results
- `GET /api/jobs/{job_id}/images/{index}` — cropped structure PNG
- `GET /api/jobs/{job_id}/download` — results as CSV
- `GET /api/health` — liveness + whether MolScribe is loaded
