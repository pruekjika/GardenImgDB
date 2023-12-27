import shutil
import os
from img_setting import SettingManager
from log_setup import logger

desktop = os.path.expanduser("~\Desktop")


def join_folder_path(_path, _filename):
    return os.path.join(_path, _filename)


def move_and_rename(old_path, new_path, new_name, extension=".jpg"):
    new_name = str(new_name)
    new_name = f"{new_name}{extension}"
    path_with_name = join_folder_path(new_path, new_name)
    shutil.move(old_path, path_with_name)


def get_sk_img_files_list(SK_PATH=f"{desktop}\SK"):
    print(SK_PATH)
    SettingManager.change_working_path(SK_PATH)
    cwd = os.getcwd()
    files = os.listdir(cwd)
    # files.sort(key=os.path.getctime)
    files = sorted(files)

    # this still is not date taken but good enough // NOT USE METADATA YET
    full_file_path = [
        os.path.join(cwd, f) for f in files if os.path.isfile(os.path.join(cwd, f))
    ]
    print(full_file_path)

    logger.info(f"move target {files}")

    return full_file_path


def move_use_list(SK_path_list, target_path, new_name):
    # not need plus 1 because now it have ref as +1
    new_name = int(new_name)

    for index, image in enumerate(SK_path_list):
        move_and_rename(image, target_path[index], str(new_name))
        logger.info(f"Move {image} to {target_path[index]} as {new_name} ")


def move_sk_to_main_folder(jpeg_count):
    jpeg_count_today_name = jpeg_count + 1
    print(jpeg_count_today_name)

    path_move_to = ["", "Zoom-1-Top", "Zoom-2-Middle", "Zoom-3-Bottom"]
    sk_path_list = get_sk_img_files_list()

    SettingManager.change_to_test()
    move_use_list(sk_path_list, path_move_to, jpeg_count_today_name)


def main():
    # move_and_rename(old_path, new_path, new_name)
    path_move_to = ["", "Zoom-1-Top", "Zoom-2-Middle", "Zoom-3-Bottom"]

    def test():
        sk_path_list = get_sk_img_files_list()
        SettingManager.change_to_test()
        move_use_list(sk_path_list, path_move_to, 17)

    # test()


if __name__ == "__main__":
    # main()
    get_sk_img_files_list()
