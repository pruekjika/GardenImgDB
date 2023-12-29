from Util.me_logger import logger
from Util.folder_util import (
    count_image_file,
    get_relative_path as gp,
    move_and_rename,
    move_first_jpg_image_to_new_path,
    find_first_jpg_with_prefix,
    join_folder_path,
)

img_fixed_path = "ImageDB\Fixed"
img_original_path = "ImageDB\Original"

img_small = "NowImage-Resized"
img_to_fixed = "NowImage-ToMatch-BIG"

img_already_fixed_count = count_image_file(gp(img_fixed_path), "*.webp")
img_original_count = count_image_file(gp(img_original_path), "*.jpg")


def validate_image_count():
    if img_already_fixed_count != img_original_count:
        logger.error(
            f"ImageDB count error: {img_already_fixed_count} != {img_original_count}"
        )


def main():
    # move_first_jpg_image_to_new_path(
    #     gp(img_small), gp(img_original_path), str(img_original_count + 1)
    # )

    print(find_first_jpg_with_prefix(gp(img_to_fixed)))


# rename


if __name__ == "__main__":
    main()
