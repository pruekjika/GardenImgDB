"""Write <folder>/index.json: the photo list the CompareWeb site reads instead of
calling the GitHub API (which is rate-limited to 60 requests/hour per visitor).

Format: [{"name": "0.webp", "date": "2023:05:12 10:11:12"}, ...] in number order.
"date" is the photo's EXIF DateTimeOriginal, or null when the photo has none.

    python PythonScpt/Util/image_index.py ImageDB
"""

import json
import sys
from pathlib import Path

from PIL import Image

IMAGE_SUFFIXES = (".webp", ".jpg", ".jpeg", ".png")
EXIF_IFD = 0x8769
DATE_TIME_ORIGINAL = 36867
DATE_TIME = 306


def photo_date(path):
    with Image.open(path) as img:
        exif = img.getexif()
    return exif.get_ifd(EXIF_IFD).get(DATE_TIME_ORIGINAL) or exif.get(DATE_TIME)


def write_image_index(folder):
    folder = Path(folder)
    photos = [p for p in folder.iterdir()
              if p.is_file() and p.suffix.lower() in IMAGE_SUFFIXES and not p.name.startswith("__")]
    photos.sort(key=lambda p: (0, int(p.stem), "") if p.stem.isdigit() else (1, 0, p.stem))
    entries = [{"name": p.name, "date": photo_date(p)} for p in photos]
    index_path = folder / "index.json"
    index_path.write_text(
        "[\n" + ",\n".join(json.dumps(entry, ensure_ascii=False) for entry in entries) + "\n]\n",
        encoding="utf-8",
    )
    return index_path, entries


if __name__ == "__main__":
    path, written = write_image_index(sys.argv[1] if len(sys.argv) > 1 else "ImageDB")
    undated = [entry["name"] for entry in written if not entry["date"]]
    print(f"{path}: {len(written)} photos" + (f", no date: {undated}" if undated else ""))
