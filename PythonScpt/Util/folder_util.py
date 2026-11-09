from pathlib import Path

IMAGE_PATTERNS = ("*.jpg", "*.webp")


def find_reference_image(folder):
    """The reference is the image whose name starts with "__"."""
    return _first_image(folder, is_reference=True)


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
