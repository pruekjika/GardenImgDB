from Util.me_logger import logger
from pathlib import Path
import glob
import shutil
import os


def create_folder(folder_path):
    Path(folder_path).mkdir(parents=True, exist_ok=True)


def join_folder_path(_path, _filename):
    return os.path.join(_path, _filename)


def get_relative_path(_path):
    return os.path.join(os.getcwd(), _path)


def get_joined_path(_path, _bad, _ref):
    _final_bad = join_folder_path(_path, _bad)
    _final_ref = join_folder_path(_path, _ref)
    return _final_bad, _final_ref


def move_folder_and_rename(old_path, new_path, new_name, extension=".jpg"):
    new_name = str(new_name)
    new_name = f"{new_name}{extension}"
    path_with_name = join_folder_path(new_path, new_name)
    shutil.move(old_path, path_with_name)


def count_image_file(path, file_extension="*.jpg") -> int:
    """
    Args:
        path (str): path
        file_extension (str, optional):. Defaults to "*.jpg".
    Returns:
        int: number of .jpg found
    """
    print(f"counting image files from {path} - {file_extension}")
    return len(glob.glob1(path, file_extension))


def change_working_path(new_path):
    os.chdir(new_path)
    logger.info(f"Change Dir To: '{os.getcwd()}'")


def move_and_rename(old_path, new_path, new_name, extension=".jpg"):
    new_name = f"{new_name}{extension}"
    path_with_name = join_folder_path(new_path, new_name)
    shutil.move(old_path, path_with_name)
    logger.info(f"move'{old_path} to {path_with_name}'")


def find_first_jpg_file(directory):
    directory_path = Path(directory)

    # Find all files with the .jpg extension in the directory
    jpg_files = directory_path.glob("*.jpg")

    # Return the path of the first jpg file found, or None if no file is found
    for file in jpg_files:
        return str(file.absolute())

    return None


def find_ref_img(directory):
    jpg_files = Path(directory).glob("*.jpg")
    for file in jpg_files:
        if file.name.startswith("__"):
            return str(file.absolute())
    return None


def find_to_fixed_img(directory):
    jpg_files = Path(directory).glob("*.jpg")
    for file in jpg_files:
        if not file.name.startswith("__"):
            return str(file.absolute())
    return None


def move_first_jpg_image_to_new_path(old_folder_path, new_path, new_name):
    print(old_folder_path)
    if find_first_jpg_file(old_folder_path) is None:
        logger.error(f"No jpg found in {old_folder_path}!!!")
        return

    move_and_rename(find_first_jpg_file(old_folder_path), new_path, new_name)


def get_filename_only(path):
    return Path(path).stem


def find_and_delete_jpg_in_folder(path):
    img_path = find_first_jpg_file(path)
    if img_path is None:
        return
    Path(img_path).unlink()
    logger.info(f"remove {img_path}!")
