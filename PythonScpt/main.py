"""Align the one photo in P-FixingImg-big onto the newest earlier ImageDB photo (already
in the master frame), then save it as ImageDB/<number>.webp with the photo's metadata.
A "__" image in P-FixingImg-big overrides the reference."""

from pathlib import Path

from Util.folder_util import db_path_for, find_image_to_fix, find_reference_image
from Util.image_index import write_image_index
from Util.me_logger import logger
from img_matcher import MatchConfig, create_fix_image, save_with_metadata

FIXING_FOLDER = Path("P-FixingImg-big")
DELETE_PREVIOUS_OUTPUTS = True
OVERWRITE_EXISTING_DB_IMAGE = False
CONFIG = MatchConfig(
    work_width=1600,
    search_radius_fraction=0.15,
    ecc_hires_width=3200,
)


def main():
    photo = find_image_to_fix(FIXING_FOLDER)
    if photo is None:
        logger.error(f"put the new photo in {FIXING_FOLDER}")
        return
    ref = find_reference_image(FIXING_FOLDER, photo)
    if ref is None:
        logger.error("no reference: ImageDB has no earlier photo and no '__' image is in the folder")
        return
    db_path = db_path_for(photo)
    if not photo.stem.isdigit():
        photo = photo.rename(photo.with_stem(db_path.stem))
        logger.info(f"renamed the photo to {photo.name} so reruns keep the same ImageDB number")
    if db_path.exists() and not OVERWRITE_EXISTING_DB_IMAGE:
        logger.error(f"{db_path} already exists; rename the photo or set OVERWRITE_EXISTING_DB_IMAGE = True")
        return

    out_dir = Path.cwd()
    if DELETE_PREVIOUS_OUTPUTS:
        for previous in out_dir.glob("__*.jpg"):
            previous.unlink()

    try:
        result, aligned = create_fix_image(ref, photo, out_dir, CONFIG)
    except RuntimeError as error:
        logger.error(str(error))
        return
    save_with_metadata(db_path, aligned, photo)
    index_path, _ = write_image_index(db_path.parent)
    logger.info(f"updated {index_path}")
    logger.info(
        f"done: {db_path} saved (stage={result.stage} score={result.score:.4f}). Open the _check.jpg to verify; "
        "if it is off, run: python PythonScpt/manual_match.py"
    )


if __name__ == "__main__":
    main()
