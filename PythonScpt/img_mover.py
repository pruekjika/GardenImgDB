from pathlib import Path
from Util.folder_util import (
    count_image_file,
    get_relative_path as gp,
    move_first_match_image_to_new_path,
)

img_fixed_path = r"ImageDB\Fixed"
img_original_path = r"ImageDB\Original"

img_small = r"P-Original-resized"
img_to_fixed = r"P-FixingImg-big"

img_already_fixed_count = count_image_file(gp(img_fixed_path), "*.webp")
img_original_count = count_image_file(gp(img_original_path), "*.jpg")


#  new workflow not use anymore
def main():
    move_first_match_image_to_new_path(
        gp(img_small), gp(img_original_path), str(img_original_count + 1), "*.jpg"
    )

    # no need +1 cause have __0.webp
    move_first_match_image_to_new_path(
        gp(Path.cwd()),
        gp(img_fixed_path),
        f"__{str(img_already_fixed_count)}",
        "*.webp",
    )


if __name__ == "__main__":
    main()
