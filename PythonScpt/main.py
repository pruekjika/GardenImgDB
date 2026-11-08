from Util.me_logger import logger
from Util.folder_util import (
    get_relative_path as gp,
    find_ref_img,
    find_to_fixed_img,
)
from img_matcher import create_fix_image, MatchConfig
from pathlib import Path

img_to_fixed = r"P-FixingImg-big"

###############################################################################
# change below
DELETE_OLD_IMG = True  # delete previous "__*.jpg" outputs in the working folder
CONFIG = MatchConfig(
    work_width=1600,  # matching resolution; raise (e.g. 2400) if result is slightly off
    search_radius=0.15,  # how far (fraction of width) framing may differ between shots
    ecc_full_width=3200,  # extra fine pass at this width; 0 = skip (faster)
)
# end need to change
###############################################################################


def main():
    ref = find_ref_img(gp(img_to_fixed))
    to_fix = find_to_fixed_img(gp(img_to_fixed))

    if ref is None or to_fix is None:
        logger.error(f"ref:{ref} / to_fix:{to_fix} one of this is NONE")
        return

    out_dir = Path.cwd()
    if DELETE_OLD_IMG:
        for old in out_dir.glob("__*.jpg"):
            old.unlink()

    try:
        result = create_fix_image(ref, to_fix, out_dir, CONFIG)
    except RuntimeError as e:
        logger.error(str(e))
        return

    logger.info(
        f"done: stage={result.stage} score={result.score:.4f} - open the _check.jpg to verify. "
        "If it is off, run: python PythonScpt/manual_match.py"
    )


if __name__ == "__main__":
    main()
