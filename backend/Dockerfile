# Backend image for Hugging Face Spaces (Docker SDK).
# HF Spaces runs the container as a non-root user (uid 1000) and routes traffic to
# the port declared as `app_port` in README.md (7860 here).
FROM python:3.10-slim

# OpenCV (cv2) needs libgl1/libglib; RDKit's Cairo PNG rendering needs the cairo/pango libs.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
 && rm -rf /var/lib/apt/lists/*

# Match HF Spaces' runtime user so files we create are writable there.
RUN useradd -m -u 1000 user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    MOLSCRIBE_MODEL_PATH=/home/user/app/models/molscribe/swin_base_char_aux_1m680k.pth \
    MODEL_DEVICE=cpu \
    TMP_DIR=/home/user/app/tmp \
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false

USER user
WORKDIR /home/user/app

COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# Bake the ~1GB MolScribe checkpoint into the image so cold starts don't redownload.
RUN pip install --no-cache-dir "huggingface_hub==0.24.6" \
 && python -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='yujieq/MolScribe', filename='swin_base_char_aux_1m680k.pth', local_dir='models/molscribe')"

COPY --chown=user app ./app

EXPOSE 7860
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
