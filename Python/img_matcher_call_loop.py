from img_matcher import *
from img_class import *


def call_loop_image(obj_loop: SettingForLoop):
    obj_loop.write_log()
    for i in range(obj_loop.loop_count):
        create_fix_image(
            obj_loop.ref_name,
            f"{obj_loop.bad_name}{i+1}",
            obj_loop.folder_in_src,
            obj_loop.folder_out_src,
            good_factor=obj_loop.good_factor,
            keypoint=obj_loop.orb_keypoint,
        )


def call_array_img(obj_array: SettingForArray):
    obj_array.write_log()

    if type(obj_array) is list:
        for i in obj_array.target_array:
            create_fix_image(
                obj_array.ref_name,
                f"{obj_array.bad_name}{i}",
                obj_array.folder_in_src,
                obj_array.folder_out_src,
                good_factor=obj_array.good_factor,
                keypoint=obj_array.orb_keypoint,
            )
    else:
        create_fix_image(
            obj_array.ref_name,
            f"{obj_array.bad_name}{obj_array.target_array}",
            obj_array.folder_in_src,
            obj_array.folder_out_src,
            good_factor=obj_array.good_factor,
            keypoint=obj_array.orb_keypoint,
        )


def main():
    pass


if __name__ == "__main__":
    main()
