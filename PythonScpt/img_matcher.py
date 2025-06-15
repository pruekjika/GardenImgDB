from Util.me_logger import logger
from Util.folder_util import create_folder, get_joined_path, join_folder_path
from img_metadata import copy_metadata_from_to
import cv2
import numpy as np


def debug_show_img(_img_b_g, _kp_b, _img_r_g, _kp_r, _matches, _showmatch_num=100):
    def show_small_img(window_name, img_src):
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        img_small = cv2.resize(img_src, (960, 540))
        cv2.imshow(window_name, img_small)

    print("Showing debug img....")
    # img_bad_final = cv2.drawKeypoints(_img_b_g, _kp_b, None, flags=None)
    # img_ref_final = cv2.drawKeypoints(_img_r_g, _kp_r, None, flags=None)

    img_match = cv2.drawMatches(
        _img_b_g, _kp_b, _img_r_g, _kp_r, _matches[:_showmatch_num], None
    )

    # show_small_img("bad_final", img_bad_final)
    # show_small_img("ref_final", img_ref_final)

    show_small_img("matches", img_match)
    # show_small_img("fix bad img", _img_b_fixed)

    cv2.waitKey(0)
    return


def create_fix_image(
    ref_img_name: str,
    bad_img_name: str,
    folder_in_path: str,
    folder_out_path: str,
    good_factor=0.01,
    file_extension=".jpg",
    keypoint=16000,
    debug=False,
    leadWord="__",
):
    """
    Keyword arguments:
    - ref_img_name
    - bad_img_name
    - new_folder_name
    - file_extension
    - keypoint
    """

    def read_img(img_name):
        return cv2.imread(img_name + file_extension)

    def img_to_grey(img):
        if img is None:
            print(f"img name: {img} ERROR! ")
            raise Exception("cannot read img, EXIT software")
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    def create_matches(des_bad, des_ref):
        matcher = cv2.DescriptorMatcher_create(
            cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING
        )
        matches = matcher.match(des_bad, des_ref, None)
        return sorted(matches, key=lambda x: x.distance, reverse=False)

    def create_npzero_with_matches_len(_matches):
        return np.zeros((len(_matches), 2), dtype=np.float32)

    def select_top_value(_matches, _good_factor):
        # this mean it will select only top 0.1 percent
        numGoodMatch = int(len(_matches) * _good_factor)
        return _matches[:numGoodMatch]

    def print_after_write_img(_fixed_name):
        logger.info(f"[{_fixed_name}] created!")

    def write_fixed_img(fixed_img):
        output_img_name = f"{leadWord}{bad_img_name}{file_extension}"  # __w3.jpg
        create_folder(folder_out_path)

        final_bad_path_name = join_folder_path(folder_out_path, output_img_name)
        cv2.imwrite(final_bad_path_name, fixed_img)
        print_after_write_img(final_bad_path_name)
        return final_bad_path_name

    logger.info(
        f"fixing: ref: '{ref_img_name}' fix: '{bad_img_name}' key: '{keypoint}' fac: '{good_factor}'"
    )

    bad_img_path, ref_img_path = get_joined_path(
        folder_in_path, bad_img_name, ref_img_name
    )
    # read and convert img
    print(f"bad:{bad_img_path} | ref:{ref_img_path}")
    img_b = read_img(bad_img_path)
    img_r = read_img(ref_img_path)

    img_b_g = img_to_grey(img_b)
    img_r_g = img_to_grey(img_r)

    orb = cv2.ORB_create(keypoint)

    kp_b, des_b = orb.detectAndCompute(img_b_g, None)
    kp_r, des_r = orb.detectAndCompute(img_r_g, None)

    matches = create_matches(des_b, des_r)
    matches = select_top_value(matches, good_factor)

    # ransac - filter bad keypoint
    point1 = create_npzero_with_matches_len(matches)
    point2 = create_npzero_with_matches_len(matches)

    for i, match in enumerate(matches):
        point1[i, :] = kp_b[match.queryIdx].pt
        point2[i, :] = kp_r[match.trainIdx].pt

    homo, mask = cv2.findHomography(point1, point2, cv2.RANSAC)

    # use homography
    ref_height, ref_width, channels = img_r.shape

    # create img
    img_b_fixed = cv2.warpPerspective(img_b, homo, (ref_width, ref_height))

    new_fix_img_path = write_fixed_img(img_b_fixed)
    print(f"bad_img_path: {bad_img_path}, new_img_path:{new_fix_img_path}")

    copy_metadata_from_to(bad_img_path + file_extension, new_fix_img_path)

    if debug:
        debug_show_img(img_b_g, kp_b, img_r_g, kp_r, img_b_fixed)


def main():
    pass


if __name__ == "__main__":
    main()
