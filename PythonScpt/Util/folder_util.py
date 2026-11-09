from pathlib import Path

IMAGE_PATTERNS = ("*.jpg", "*.webp")


def find_reference_image(folder):
    """The reference is the image whose name starts with "__"."""
    return _first_image(folder, is_reference=True)


def find_image_to_fix(folder):
    return _first_image(folder, is_reference=False)


def _first_image(folder, is_reference):
    for pattern in IMAGE_PATTERNS:
        for file in Path(folder).glob(pattern):
            if file.name.startswith("__") == is_reference:
                return file.resolve()
    return None
