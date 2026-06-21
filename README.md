# comic-translate-catalog

CLI для пакетного перевода изображений из каталога.

## Структура

```
translate_catalog/
├── translate_catalog.py     # CLI entry point
├── app/                     # движок
├── data/                    # для фильтрации слов перевода
├── models/                  # сюда класть .gguf
├── requirements.txt         # CLI-зависимости
├── install.sh               # .venv + pip install
├── download-model.sh        # скачать GGUF
├── result/                  # создаётся при первом запуске
```

## Установка

```bash
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
| `--source LANG` | Исходный язык (`en`, `ru`, `ch`, `japan`, `korean`, …) |
| `--target LANG` | Целевой язык: `ru`/`rus`/`Russian`, `en`/`eng`/`English`, … |
| `--out DIR` | Корневая папка результатов (default: `./result`) |
| `--format EXT` | Расширение выходных файлов: `png` / `jpg` / `webp` (default: `png`) |

### Поддерживаемые входные форматы

`.png`, `.jpg`, `.jpeg`, `.webp`, `.bmp`, `.tif`, `.tiff`, `.gif`.

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
    --in "/path/to/images" \
    --source en \
    --target rus
```

Результат: `result/[BDOne] Prince_ Chapter_translate/` с 26 PNG (по числу .webp).


## Отладка

По умолчанию CLI печатает только прогресс по картинкам и итоговую сводку.
Для диагностики (cache hits, per-block source/translated, meta JSON,
inpaint details) включите debug-режим:

```bash
TRANSLATE_DEBUG=1 python translate_catalog.py \
    --in "/path/to/images" \
    --source en \
    --target rus
```

Допустимые значения: `1`, `true`, `yes`, `on` (регистр не важен).
