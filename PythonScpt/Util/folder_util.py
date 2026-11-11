from pathlib import Path

IMAGE_PATTERNS = ("*.jpg", "*.webp")

# Every new photo is matched to this one fixed ImageDB photo, so errors never chain from photo
# to photo. All ImageDB photos sit in master 61's frame (batch_align.py joint solve, 2026-11-11),
# so the result lands in that frame too. Not 61 itself: 2026 photos matched straight onto 61
# (Dec 2022, older garden layout) came out ~800 px off; onto 91 (2025-12-31) they stay under ~13 px.
REFERENCE_NUMBER = 91


def find_reference_image(folder, image_db=Path("ImageDB")):
    """A "__" image in folder wins (one-off override), else ImageDB/<REFERENCE_NUMBER>.webp."""
    return _first_image(folder, is_reference=True) or (image_db / f"{REFERENCE_NUMBER}.webp").resolve()


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
