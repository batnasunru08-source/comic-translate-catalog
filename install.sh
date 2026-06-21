#!/bin/bash
# Установка зависимостей для translate_catalog (CLI).
#
# Стратегия: uv + prebuilt wheels от abetlen (cu130), без локальной
# компиляции. Совпадает с рабочим venv сервера (torch 2.12.0+cu130).
# На cu132 есть регресс с импортом torch на этой системе (драйвер 610,
# CUDA 12.0 toolkit), поэтому cu130.
set -e
cd "$(dirname "$0")"

# ─── venv ──────────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
    echo "[INSTALL] Creating .venv..."
    python3 -m venv .venv
fi

# shellcheck disable=SC1091
source .venv/bin/activate

# ─── uv (быстрая замена pip) ────────────────────────────────────────
if ! command -v uv &> /dev/null; then
    echo "[INSTALL] Installing uv..."
    pip install -U uv
fi
echo "[INSTALL] uv: $(uv --version)"

# ─── Базовые зависимости + torch с CUDA 13.0 (cu130) ──────────────
echo "[INSTALL] Installing base requirements with uv..."
uv pip install -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cu130 \
    --index-strategy unsafe-best-match

# ─── llama-cpp-python: prebuilt wheel от abetlen (cu130) ───────────
# Индекс cu130 содержит wheel начиная с v0.3.25.
# https://github.com/abetlen/llama-cpp-python/releases через
# https://abetlen.github.io/llama-cpp-python/whl/cu130
if /home/batnasun/translate_catalog/.venv/bin/python -c "import llama_cpp" 2>/dev/null; then
    echo "[INSTALL] llama-cpp-python already installed, skipping."
else
    echo "[INSTALL] Installing llama-cpp-python (prebuilt cu130 wheel)..."
    uv pip install "llama-cpp-python==0.3.25" \
        --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu130 \
        --index-strategy unsafe-best-match
fi

# ─── Sanity check ──────────────────────────────────────────────────
/home/batnasun/translate_catalog/.venv/bin/python - <<'PY'
import sys
print(f"[INSTALL] python: {sys.version.split()[0]}")
import torch
print(f"[INSTALL] torch: {torch.__version__} cuda_available={torch.cuda.is_available()}")
import llama_cpp
print(f"[INSTALL] llama_cpp: {llama_cpp.__version__ if hasattr(llama_cpp, '__version__') else 'unknown'}")
import os
libs = os.listdir(os.path.join(os.path.dirname(llama_cpp.__file__), "lib"))
cuda = any("cuda" in l for l in libs)
print(f"[INSTALL] CUDA backend: {'yes' if cuda else 'no (CPU only)'}")
PY

echo
echo "[INSTALL] Done. Next:"
echo "  source .venv/bin/activate"
echo "  bash download-model.sh            # 1.8B Q8_0 (default, ~1.9 GB)"
echo "  bash download-model.sh 7b         # 7B   Q8_0 (~8.0 GB)"
echo "  python translate_catalog.py --in <DIR> --source en --target rus"

