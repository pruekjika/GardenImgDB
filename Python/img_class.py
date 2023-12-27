from log_setup import logger
import img_setting


class MatchSetting:
    def __init__(
        self,
        ref_name: str,
        bad_name: str,
        folder_in_src: str,
        folder_out_src: str,
        orb_keypoint: int,
        good_factor: float,
        debug: bool = False,
    ) -> None:
        self.ref_name = ref_name
        self.bad_name = bad_name
        self.folder_in_src = folder_in_src
        self.folder_out_src = folder_out_src
        self.orb_keypoint = orb_keypoint
        self.good_factor = good_factor
        self.debug = debug

    def write_json_setting(self, json_write_path: str):
        img_setting.SettingManager.save_setting(self, json_write_path)


class SettingForLoop(MatchSetting):
    def __init__(
        self,
        ref_name: str,
        bad_name: str,
        folder_in_src: str,
        folder_out_src: str,
        loop_count: int,
        orb_keypoint: int,
        good_factor: float,
        debug: bool = False,
    ) -> None:
        super().__init__(
            ref_name,
            bad_name,
            folder_in_src,
            folder_out_src,
            orb_keypoint,
            good_factor,
            debug,
        )
        self.loop_count = loop_count

    def write_log(self):
        # logger.info("- do loop -")
        logger.info(vars(self))


class SettingForArray(MatchSetting):
    def __init__(
        self,
        ref_name: str,
        bad_name: str,
        folder_in_src: str,
        folder_out_src: str,
        target_array,
        orb_keypoint: int,
        good_factor: float,
        debug: bool = False,
    ) -> None:
        super().__init__(
            ref_name,
            bad_name,
            folder_in_src,
            folder_out_src,
            orb_keypoint,
            good_factor,
            debug,
        )
        self.target_array = target_array

    def write_log(self):
        # logger.info("- do array -")
        logger.info(vars(self))


def main():
    array_test = SettingForArray(
        "8",
        "",
        r"C:\Users\meang\Desktop\TestData",
        r"C:\Users\meang\Desktop\TestData\FixImg\0-main-fix",
        [16],
        90000,
        0.01,
    )
    array_test.write_json_setting("__test.json")


if __name__ == "__main__":
    main()
