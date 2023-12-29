from pathlib import Path
import os


def create_folder(folder_path):
    Path(folder_path).mkdir(parents=True, exist_ok=True)


def join_folder_path(_path, _filename):
    return os.path.join(_path, _filename)


def get_joined_path(_path, _bad, _ref):
    _final_bad = join_folder_path(_path, _bad)
    _final_ref = join_folder_path(_path, _ref)
    return _final_bad, _final_ref
