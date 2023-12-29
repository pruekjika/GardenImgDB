from log_setup import logger
from pathlib import Path
import glob
import shutil
import os


def create_folder(folder_path):
    Path(folder_path).mkdir(parents=True, exist_ok=True)


def join_folder_path(_path, _filename):
    return os.path.join(_path, _filename)


def get_joined_path(_path, _bad, _ref):
    _final_bad = join_folder_path(_path, _bad)
    _final_ref = join_folder_path(_path, _ref)
    return _final_bad, _final_ref


def move_folder_and_rename(old_path, new_path, new_name, extension=".jpg"):
    new_name = str(new_name)
    new_name = f"{new_name}{extension}"
    path_with_name = join_folder_path(new_path, new_name)
    shutil.move(old_path, path_with_name)


def jpg_counter(path, file_extension="*.jpg") -> int:
    """
    Args:
        path (str): path
        file_extension (str, optional):. Defaults to "*.jpg".
    Returns:
        int: number of .jpg found
    """
    return len(glob.glob1(path, file_extension))


def change_working_path(new_path):
    os.chdir(new_path)
    logger.info(f"Change Dir To: '{os.getcwd()}'")
