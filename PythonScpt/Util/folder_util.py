from pathlib import Path

IMAGE_PATTERNS = ("*.jpg", "*.webp")

# Every ImageDB photo is aligned to master photo 61 (batch_align.py, 2026-11-11), so any of
# them is a reference in the master frame. None = the newest ImageDB photo before the new one:
# closest in season and layout, which matches far better than the old master (a direct
# cross-season match to the master was ~90 px off at the corners). A number = always that photo.
REFERENCE_NUMBER = None


def find_reference_image(folder, photo=None, image_db=Path("ImageDB")):
    """A "__" image in folder wins (manual override), then REFERENCE_NUMBER, then the newest
    ImageDB photo numbered before this photo."""
    ref = _first_image(folder, is_reference=True)
    if ref is not None:
        return ref
    if REFERENCE_NUMBER is not None:
        return (image_db / f"{REFERENCE_NUMBER}.webp").resolve()
    limit = int(db_path_for(photo, image_db).stem) if photo is not None else float("inf")
    numbers = [int(p.stem) for p in image_db.glob("*.webp") if p.stem.isdigit() and int(p.stem) < limit]
    return (image_db / f"{max(numbers)}.webp").resolve() if numbers else None


def find_image_to_fix(folder):
    return _first_image(folder, is_reference=False)


def db_path_for(photo, image_db=Path("ImageDB")):
    """A numbered photo (97.JPG) keeps its number; any other name gets the next free number,
    so give it that number before a rerun or the rerun picks a new one."""
    if photo.stem.isdigit():
        return image_db / f"{int(photo.stem)}.webp"
    numbers = [int(p.stem) for p in image_db.glob("*.webp") if p.stem.isdigit()]
    return image_db / f"{max(numbers, default=-1) + 1}.webp"


def _first_image(folder, is_reference):
    for pattern in IMAGE_PATTERNS:
        for file in Path(folder).glob(pattern):
            if file.name.startswith("__") == is_reference:
                return file.resolve()
    return None
