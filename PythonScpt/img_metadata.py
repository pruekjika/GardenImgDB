from PIL import Image
from Util.me_logger import logger


def copy_metadata_from_to(from_path, to_path, new_path=None):
    """if it have new_path it will create new file

    Args:
        from_path (str): file that contain metadata
        to_path (str): target image
        new_path (str, optional): in case I want it in new file. Defaults to None.
    """

    def save_img(_img_to_save, _img_path, do_log=False):
        _img_to_save.save(_img_path, "JPEG", exif=exif)

        if do_log:
            logger.info(
                f"copy metadata from {from_path} | use img {to_path} to {_img_path}"
            )

    image_ref = Image.open(from_path)
    exif = image_ref.info["exif"]
    image_new = Image.open(to_path)

    save_img(image_new, to_path) if new_path is None else save_img(image_new, new_path)


def compare_webp_to_jpg_name(webp_name, jpg_name):
    real_webp = webp_name.replace("__", "").replace(".webp", "")
    real_jpg = jpg_name.replace(".webp", "")
    if real_webp == real_jpg:
        return True
    else:
        return False


def main():
    f_path_1 = r"C:\Users\meang\Desktop\TestData\9.JPG"
    f_path_2 = r"C:\Users\meang\Desktop\TestData\8.JPG"
    copy_metadata_from_to(f_path_1, f_path_2)


if __name__ == "__main__":
    main()
