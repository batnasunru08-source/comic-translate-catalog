#!/usr/bin/env python3
"""CLI для пакетного перевода изображений из каталога через vendored app/.

Использование:
    python translate_catalog.py --in <DIR> --source en --target rus
    python translate_catalog.py --in <DIR> --source en --target Russian --out ./out
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tempfile
import time
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from app.pipeline import process_image_bytes


_TARGET_ALIASES: dict[str, str] = {
    "ru": "Russian", "rus": "Russian", "russian": "Russian",
    "en": "English", "eng": "English", "english": "English",
    "zh": "Chinese", "ch": "Chinese", "chinese": "Chinese",
    "ja": "Japanese", "japan": "Japanese", "japanese": "Japanese",
    "ko": "Korean", "korean": "Korean",
    "fr": "French", "fra": "French", "french": "French",
    "de": "German", "deu": "German", "german": "German",
    "es": "Spanish", "spa": "Spanish", "spanish": "Spanish",
    "pt": "Portuguese", "por": "Portuguese", "portuguese": "Portuguese",
    "it": "Italian", "ita": "Italian", "italian": "Italian",
    "tr": "Turkish", "tur": "Turkish", "turkish": "Turkish",
    "ar": "Arabic", "ara": "Arabic", "arabic": "Arabic",
    "th": "Thai", "tha": "Thai", "thai": "Thai",
    "vi": "Vietnamese", "vie": "Vietnamese", "vietnamese": "Vietnamese",
    "pl": "Polish", "pol": "Polish", "polish": "Polish",
    "nl": "Dutch", "nld": "Dutch", "dutch": "Dutch",
    "cs": "Czech", "ces": "Czech", "czech": "Czech",
    "hi": "Hindi", "hin": "Hindi", "hindi": "Hindi",
    "uk": "Ukrainian", "ukr": "Ukrainian", "ukrainian": "Ukrainian",
}

_IMAGE_EXTS: frozenset[str] = frozenset(
    {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff", ".gif"}
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Пакетный перевод изображений из каталога через vendored app/."
    )
    parser.add_argument("--in", dest="in_dir", required=True,
                        help="Каталог с изображениями (только верхний уровень).")
    parser.add_argument("--source", required=True,
                        help="OCR язык (en, ru, ch, japan, korean, ...).")
    parser.add_argument("--target", required=True,
                        help="Целевой язык: ru/rus/Russian, en/eng/English, ...")
    parser.add_argument("--out", default=str(HERE / "result"),
                        help="Корневая папка для результатов (default: ./result).")
    parser.add_argument("--format", default="png", choices=["png", "jpg", "webp"],
                        help="Расширение выходных файлов (default: png).")
    return parser.parse_args()


def resolve_target(value: str) -> str:
    full = _TARGET_ALIASES.get(value.lower())
    if full is None:
        examples = sorted({k for k in _TARGET_ALIASES if len(k) <= 3})[:8]
        print(
            f"ERROR: unknown --target {value!r}. Примеры кодов: "
            f"{', '.join(examples)}; полные имена: Russian, English, ...",
            file=sys.stderr,
        )
        sys.exit(2)
    return full


def main() -> int:
    args = parse_args()

    in_dir = Path(args.in_dir).resolve()
    if not in_dir.is_dir():
        print(f"ERROR: not a directory: {in_dir}", file=sys.stderr)
        return 2

    target_full = resolve_target(args.target)
    out_root = Path(args.out).resolve()
    out_dir = out_root / f"{in_dir.name}_translate"
    out_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(
        f for f in in_dir.iterdir()
        if f.is_file() and f.suffix.lower() in _IMAGE_EXTS
    )
    if not images:
        print(f"ERROR: no images found in {in_dir} (extensions: {sorted(_IMAGE_EXTS)})",
              file=sys.stderr)
        return 2

    print(f"[CLI] in={in_dir}")
    print(f"[CLI] source_ocr_lang={args.source} target_lang={target_full}")
    print(f"[CLI] out={out_dir} n_images={len(images)} format={args.format}")

    ok = 0
    fail = 0
    started = time.perf_counter()

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        for i, img in enumerate(images, 1):
            t0 = time.perf_counter()
            try:
                content = img.read_bytes()
                result_path, _meta = process_image_bytes(
                    content, tmp_dir,
                    source_ocr_lang=args.source,
                    target_lang=target_full,
                )
                final_path = out_dir / f"{img.stem}.{args.format}"
                shutil.move(str(result_path), str(final_path))
                ms = round((time.perf_counter() - t0) * 1000)
                print(f"[{i}/{len(images)}] {img.name} -> {final_path.name} ({ms}ms)")
                ok += 1
            except Exception as err:
                ms = round((time.perf_counter() - t0) * 1000)
                print(f"[{i}/{len(images)}] {img.name} FAILED ({ms}ms): {err}",
                      file=sys.stderr)
                traceback.print_exc()
                fail += 1

    total_ms = round((time.perf_counter() - started) * 1000)
    print(f"\n[CLI] Done: ok={ok} fail={fail} total={total_ms}ms out={out_dir}")
    return 0 if fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
