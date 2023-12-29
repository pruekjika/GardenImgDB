from Util.me_logger import logger
from Util.folder_util import (
    count_image_file,
    get_relative_path as gp,
    find_ref_img,
    find_to_fixed_img,
)
from img_matcher import create_fix_image

img_fixed_path = r"ImageDB\Fixed"
img_original_path = r"ImageDB\Original"

img_small = r"NowImage-Resized"
img_to_fixed = r"NowImage-ToMatch-BIG"

img_already_fixed_count = count_image_file(gp(img_fixed_path), "*.webp")
img_original_count = count_image_file(gp(img_original_path), "*.jpg")


def main():
    # just auto move img file
    # move_first_jpg_image_to_new_path(
    #     gp(img_small), gp(img_original_path), str(img_original_count + 1)
    # )

    ref = find_ref_img(gp(img_to_fixed))
    to_fix = find_to_fixed_img(gp(img_to_fixed))
    if ref is None or to_fix is None:
        logger.error(f"ref:{ref} / to_fix:{to_fix} one of this is NONE")
        return

    create_fix_image(ref, to_fix, gp(img_to_fixed), gp(img_fixed_path), debug=True)


if __name__ == "__main__":
    main()
