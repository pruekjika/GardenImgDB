import json
import glob
import os
import img_class
from log_setup import logger


class SettingManager:
    """_summary_
    the json should be in one big object then save it only one time
    """

    test_path = r"C:\Users\meang\Desktop\TestData"
    work_path = r"C:\Users\meang\Desktop\GardenMap-database"

    json_file_path = r"D:\Github\P.image-matching\match_setting.json"

    def log_change_dir():
        logger.info(f"WORKING DIR: '{os.getcwd()}'")

    def change_working_path(new_path):
        os.chdir(new_path)

    def change_to_test():
        SettingManager.change_working_path(SettingManager.test_path)
        SettingManager.log_change_dir()

    def change_to_real_work():
        SettingManager.change_working_path(SettingManager.work_path)
        SettingManager.log_change_dir()

    def check_if_list(to_check):
        return True if isinstance(to_check) is list else False

    @staticmethod
    def save_setting(matchSetting, json_write_path: str = json_file_path):
        """receive matchSetting as array

        Args:
            json_write_path (str): path to write
            matchSetting (_type_): setting to write
        """

        def save_list():
            logger.info(f"save new LIST-setting to {json_write_path}")
            json_from_list = json.dumps([ob.__dict__ for ob in matchSetting], indent=2)
            with open(json_write_path, "w", encoding="utf-8") as file:
                file.write(json_from_list)

        def save_one_setting():
            logger.info(f"save new ONE-setting to {json_write_path}")
            json_from_list = json.dumps(matchSetting.__dict__, indent=2)
            with open(json_write_path, "w", encoding="utf-8") as file:
                file.write(json_from_list)

        if SettingManager.check_if_list(matchSetting):
            save_list()
        else:
            save_one_setting()

    @staticmethod
    def load_setting(json_path: str = json_file_path):
        def load_list_data(_json_data):
            all_setting = []
            for obj in _json_data:
                setting_data_python = img_class.SettingForArray(**obj)
                all_setting.append(setting_data_python)
            return all_setting

        with open(json_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

            if SettingManager.check_if_list(json_data):
                return load_list_data(json_data)
            else:
                return img_class.SettingForArray(**json_data)

    @staticmethod
    def load_setting_loop(json_path: str = json_file_path):
        def load_list_data(_json_data):
            all_setting = []
            for obj in _json_data:
                setting_data_python = img_class.SettingForLoop(**obj)
                all_setting.append(setting_data_python)
            return all_setting

        with open(json_path, "r", encoding="utf-8") as file:
            json_data = json.load(file)

            if SettingManager.check_if_list(json_data):
                return load_list_data(json_data)
            else:
                return img_class.SettingForLoop(**json_data)

    @staticmethod
    def jpg_counter(path) -> int:
        return len(glob.glob1(path, "*.jpg"))

    @staticmethod
    def update_setting_target_array_to_jpg_count(
        json_setting_path: str = json_file_path, jpeg_path: str = ""
    ):
        def update_to_new_value(_old_setting, _new_number):
            if SettingManager.check_if_list(_old_setting):
                new_setting = []
                for setting in _old_setting:
                    setting.target_array = _new_number
                    new_setting.append(setting)
                return new_setting
            else:
                _old_setting.target_array = _new_number
                return _old_setting

        # count nolonger need +1 because it auto plus 1 from ref
        new_number = SettingManager.jpg_counter(jpeg_path)
        # becaue it count ref
        new_number -= 1

        old_setting = SettingManager.load_setting(json_setting_path)
        new_setting = update_to_new_value(old_setting, new_number)
        SettingManager.save_setting(new_setting)
        logger.info(f"Done update setting in {json_setting_path} to {new_number}")


def main():
    def save_test_data():
        today = [16]
        array_setting_1 = img_class.SettingForArray(
            "8", "", r"", r"FixImg\0-main-fix", today, 90000, 0.01
        )
        array_setting_2 = img_class.SettingForArray(
            "10", "", r"Zoom-1-Top", r"FixImg\1-Top-fix", today, 90000, 0.01
        )
        array_setting_3 = img_class.SettingForArray(
            "10", "", r"Zoom-2-Middle", r"FixImg\2-Middle-fix", today, 90000, 0.01
        )
        array_setting_4 = img_class.SettingForArray(
            "10", "", r"Zoom-3-Bottom", r"FixImg\3-Bottom-fix", today, 90000, 0.01
        )
        call_array = [
            array_setting_1,
            array_setting_2,
            array_setting_3,
            array_setting_4,
        ]
        SettingManager.save_setting(call_array)

    def load_test():
        wa = SettingManager.load_setting("__test.json")
        for i in wa:
            print(type(i))
            print(i.ref_name)
            print(vars(i))
            print("============================================================")

    def update_jpeg_test():
        SettingManager.update_setting_target_array_to_jpg_count()

    def realCall():
        SettingManager.change_to_test()
        # SettingManager.change_to_real_work()

        save_test_data()
        # save_test()
        # load_test()
        update_jpeg_test()

    realCall()


if __name__ == "__main__":
    main()
