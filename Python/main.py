from .LoopCall.img_matcher_call_loop import *
from .img_class import *
from .img_setting import *
from .img_mover import *


def main():
    def move_img():
        path_move_to = ["", "Zoom-1-Top", "Zoom-2-Middle", "Zoom-3-Bottom"]
        sk_path_list = get_sk_img_files_list()
        SettingManager.change_to_real_work()
        move_use_list(sk_path_list, path_move_to, SettingManager.jpg_counter(""))

    def main_process():
        move_img()

        SettingManager.change_to_real_work()
        SettingManager.update_setting_target_array_to_jpg_count()

        setting_list = SettingManager.load_setting()

        for setting in setting_list:
            call_array_img(setting)

    def fix_image():
        SettingManager.change_to_real_work()
        setting_list = SettingManager.load_setting(
            "D:\Github\P.image-matching\match_fix.json"
        )
        for setting in setting_list:
            call_array_img(setting)

    def external_process():
        SettingManager.change_working_path(r"C:\Users\meang\Downloads\Fix")
        setting_list = SettingManager.load_setting(
            r"D:\Github\P.image-matching\match_home.json"
        )

        for setting in setting_list:
            call_array_img(setting)

    def external_process_fix():
        SettingManager.change_working_path(r"C:\Users\meang\Downloads\Fix")
        setting_list = SettingManager.load_setting(
            r"D:\Github\P.image-matching\match_home_fix.json"
        )

        for setting in setting_list:
            call_array_img(setting)

    fix_image()
    # main_process()
    # external_process()
    # external_process_fix()


if __name__ == "__main__":
    main()
