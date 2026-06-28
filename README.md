# translate_catalog

CLI для пакетного перевода изображений из каталога

## Структура

```
translate_catalog/
├── translate_catalog.py     # CLI entry point
├── app/                     # Движок приложения
├── data/                    # Фильтр слов, можно добавлять вручную
├── models/                  # сюда класть .gguf
├── requirements.txt         # CLI-зависимости
├── install.sh               # .venv + pip install
├── download-model.sh        # скачать GGUF
├── result/                  # создаётся при первом запуске
└── .venv/                   # создаётся install.sh
```

## Установка

```bash
cd /home/batnasun/translate_catalog
bash install.sh
```

Создаётся `.venv`, ставятся torch, transformers, paddleocr, opencv, pillow и
`llama-cpp-python` (с CUDA если есть NVIDIA GPU).

## Скачать модель

```bash
source .venv/bin/activate
bash download-model.sh            # 1.8B Q8_0 (~1.9 GB, default)
bash download-model.sh 7b         # 7B   Q8_0 (~8.0 GB)
bash download-model.sh 1.8b q4_k_m    # 1.8B Q4_K_M (~1.1 GB)
```

Модель должна лежать в `./models/`. Можно вместо этого задать env var:
```bash
export MODEL_FILE=HY-MT2-7B-Q8_0.gguf
```

## Запуск

```bash
source .venv/bin/activate
python translate_catalog.py \
    --in "/path/to/images" \
    --source en \
    --target rus
```

### Аргументы

| Флаг | Описание |
|---|---|
| `--in DIR` | Каталог с изображениями (только верхний уровень) |
| `--source LANG` | Код OCR для PaddleOCR (`en`, `ru`, `ch`, `japan`, `korean`, …) |
| `--target LANG` | Целевой язык: `ru`/`rus`/`Russian`, `en`/`eng`/`English`, … |
| `--out DIR` | Корневая папка результатов (default: `./result`) |
| `--format EXT` | Расширение выходных файлов: `png` / `jpg` / `webp` (default: `png`) |

### Поддерживаемые входные форматы

`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tif`, `.tiff`, `.gif`.

### Поддерживаемые языки

**`--target`** — язык перевода. Принимает ISO 639-1, ISO 639-3 или полное
английское имя (модель `Hy-MT2` ожидает полное имя). 19 языков с алиасами:

| Код (`--target`) | Полное имя (модель) | Локальное |
|---|---|---|
| `ru` / `rus` | `Russian` | Русский |
| `en` / `eng` | `English` | Английский |
| `zh` / `ch` | `Chinese` | Китайский |
| `ja` / `japan` | `Japanese` | Японский |
| `ko` / `korean` | `Korean` | Корейский |
| `fr` / `fra` | `French` | Французский |
| `de` / `deu` | `German` | Немецкий |
| `es` / `spa` | `Spanish` | Испанский |
| `pt` / `por` | `Portuguese` | Португальский |
| `it` / `ita` | `Italian` | Итальянский |
| `tr` / `tur` | `Turkish` | Турецкий |
| `ar` / `ara` | `Arabic` | Арабский |
| `th` / `tha` | `Thai` | Тайский |
| `vi` / `vie` | `Vietnamese` | Вьетнамский |
| `pl` / `pol` | `Polish` | Польский |
| `nl` / `nld` | `Dutch` | Голландский |
| `cs` / `ces` | `Czech` | Чешский |
| `hi` / `hin` | `Hindi` | Хинди |

Hy-MT2 также поддерживает `Indonesian`, `Malay`, `Filipino`, `Burmese`,
`Khmer`, `Persian`, `Urdu`, `Hebrew`, `Bengali`, `Tamil`, `Telugu`, `Marathi`,
`Gujarati`, `Traditional Chinese`, `Kazakh`, `Mongolian`, `Tibetan`, `Cantonese`
и др. — передавайте полное имя напрямую: `--target Indonesian`,
`--target Traditional Chinese`.

**`--source`** — код для PaddleOCR. Полный список смотрите в документации
PaddleOCR (https://www.paddleocr.ai/latest/en/version3.x/module_usage/ocr.html).
Часто используемые: `en` (английский), `ch` / `chinese_cht` (китайский),
`japan` (японский), `korean` (корейский), `ru` (русский), `fr` (французский),
`de` (немецкий), `ar` (арабский), `hi` (хинди), `pt` (португальский),
`es` (испанский), `it` (итальянский).

### Выход

```
result/<input_dir_basename>_translate/
    01_<hash>.png
    02_<hash>.png
    ...
```

Имя файла — оригинальное (без суффиксов), расширение `.png` (или как задано).

## Пример с тестовым каталогом

```bash
python translate_catalog.py \
    --in "/path_example" \
    --source en \
    --target rus
```

Результат: `result/path_example_translate/` с 26 PNG (по числу .webp).

## Отладка

По умолчанию CLI печатает только прогресс по картинкам и итоговую сводку.
Для диагностики (cache hits, per-block source/translated, meta JSON,
inpaint details) включите debug-режим:

```bash
TRANSLATE_DEBUG=1 python translate_catalog.py \
    --in "/path_example" \
    --source en \
    --target rus
```

Допустимые значения: `1`, `true`, `yes`, `on` (регистр не важен).
