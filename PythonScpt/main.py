"""Align the one photo in P-FixingImg-big onto the "__" reference next to it."""

from pathlib import Path

from Util.folder_util import find_image_to_fix, find_reference_image
from Util.me_logger import logger
from img_matcher import MatchConfig, create_fix_image

FIXING_FOLDER = Path("P-FixingImg-big")
DELETE_PREVIOUS_OUTPUTS = True
CONFIG = MatchConfig(
    work_width=1600,
    search_radius_fraction=0.15,
    ecc_hires_width=3200,
)


def main():
    ref = find_reference_image(FIXING_FOLDER)
    photo = find_image_to_fix(FIXING_FOLDER)
    if ref is None or photo is None:
        logger.error(f"need a '__' reference and a photo in {FIXING_FOLDER} (ref: {ref}, photo: {photo})")
        return

    out_dir = Path.cwd()
    if DELETE_PREVIOUS_OUTPUTS:
        for previous in out_dir.glob("__*.jpg"):
            previous.unlink()

    try:
        result = create_fix_image(ref, photo, out_dir, CONFIG)
    except RuntimeError as error:
        logger.error(str(error))
        return
    logger.info(
        f"done: stage={result.stage} score={result.score:.4f}. Open the _check.jpg to verify; "
        "if it is off, run: python PythonScpt/manual_match.py"
    )


if __name__ == "__main__":
    main()
