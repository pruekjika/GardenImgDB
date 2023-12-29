from Util.folder_util import (
    count_image_file,
    get_relative_path as gp,
    move_first_jpg_image_to_new_path,
)

img_fixed_path = r"ImageDB\Fixed"
img_original_path = r"ImageDB\Original"

img_small = r"NowImage-Resized"
img_to_fixed = r"NowImage-ToMatch-BIG"

img_already_fixed_count = count_image_file(gp(img_fixed_path), "*.webp")
img_original_count = count_image_file(gp(img_original_path), "*.jpg")

ALLOW_PERCENT = 0.001
KEYPOINT = 200000


def main():
    move_first_jpg_image_to_new_path(
        gp(img_small), gp(img_original_path), str(img_original_count + 1)
    )


if __name__ == "__main__":
    main()
