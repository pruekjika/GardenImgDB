from Util.me_logger import logger
from Util.folder_util import (
    count_image_file,
    get_relative_path as gp,
    find_ref_img,
    find_to_fixed_img,
    get_filename_only as gn,
    find_and_delete_jpg_in_folder as do_del,
)
from img_matcher import create_fix_image
from pathlib import Path

img_fixed_path = r"ImageDB\Fixed"
img_original_path = r"ImageDB\Original"

img_to_fixed = r"P-FixingImg-big"

# todo  make it work with .webp
img_already_fixed_count = count_image_file(gp(img_fixed_path), "*.webp")
img_original_count = count_image_file(gp(img_original_path), "*.jpg")

###############################################################################
# change below
ALLOW_PERCENT = 0.005
BASE_KEYPOINT = 15000
DELETE_OLD_IMG = True
# end need to change
###############################################################################


def main():
    ref = find_ref_img(gp(img_to_fixed))
    to_fix = find_to_fixed_img(gp(img_to_fixed))

    if ref is None or to_fix is None:
        logger.error(f"ref:{ref} / to_fix:{to_fix} one of this is NONE")
        return

    if DELETE_OLD_IMG:
        do_del(Path.cwd())

    # Loop through different keypoint values: 20000, 20100, 20200, etc.
    for i in range(10):  # Creates 5 different outputs
        keypoint_value = BASE_KEYPOINT + (i * 100)
        output_prefix = f"__{keypoint_value}_"

        create_fix_image(
            gn(ref),
            gn(to_fix),
            gp(img_to_fixed),
            gp(Path.cwd()),
            ALLOW_PERCENT,
            keypoint=keypoint_value,
            leadWord=output_prefix,
        )


if __name__ == "__main__":
    main()
