"""Align a photo by clicking matching points, for when automatic matching is off.

    python PythonScpt/manual_match.py                     photo + "__" ref from P-FixingImg-big
    python PythonScpt/manual_match.py --points p.json     reuse saved points (add --edit to adjust)
    python PythonScpt/manual_match.py --photo P-Originals/40.jpg --ref P-Originals/95.jpg --out P-Aligned

Click a spot in PHOTO, then the same spot in REF; at least 4 pairs, 6-10 spread
over the whole image is better (road, building and pond corners). A zoom box
follows the cursor; windows can be maximised.
Keys: u undo, r reset, Enter/Space done, q/Esc quit.
Points are saved to <out>/__<photo>_points.json; batch_align.py picks them up.
"""

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

import img_matcher as im
from Util.folder_util import find_image_to_fix, find_reference_image
from Util.me_logger import logger

DISPLAY_WIDTH = 1800
ZOOM_HALF_SIZE = 60
ZOOM_BOX_SIZE = 240
CLICK_TOLERANCE_PX = 40.0
KEY_ENTER, KEY_RETURN, KEY_SPACE, KEY_ESC = 13, 10, 32, 27
MARKER_COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255),
                 (255, 255, 0), (0, 128, 255), (255, 128, 0), (128, 0, 255), (0, 255, 128)]


@dataclass
class View:
    image: np.ndarray
    scale: float
    points: list = field(default_factory=list)
    cursor: tuple = None


class PointPicker:
    def __init__(self, img_photo, img_ref, pairs=None):
        self.views = {}
        for name, img in (("PHOTO", img_photo), ("REF", img_ref)):
            scale = DISPLAY_WIDTH / img.shape[1]
            self.views[name] = View(cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA), scale)
        for photo_point, ref_point in pairs or []:
            self.views["PHOTO"].points.append(tuple(photo_point))
            self.views["REF"].points.append(tuple(ref_point))

    def next_window(self):
        return "PHOTO" if len(self.views["PHOTO"].points) == len(self.views["REF"].points) else "REF"

    def mouse_handler(self, name):
        def on_mouse(event, x, y, _flags, _param):
            view = self.views[name]
            view.cursor = (x, y)
            if event != cv2.EVENT_LBUTTONDOWN:
                return
            if name != self.next_window():
                logger.info(f"click in {self.next_window()} next")
                return
            view.points.append((x / view.scale, y / view.scale))
        return on_mouse

    def undo(self):
        photo_points, ref_points = self.views["PHOTO"].points, self.views["REF"].points
        if len(photo_points) > len(ref_points):
            photo_points.pop()
        elif ref_points:
            ref_points.pop()

    def reset(self):
        for view in self.views.values():
            view.points.clear()

    def pairs(self):
        return [[list(p), list(r)] for p, r in zip(self.views["PHOTO"].points, self.views["REF"].points)]

    def render(self, name):
        view = self.views[name]
        canvas = view.image.copy()
        for i, (x, y) in enumerate(view.points):
            at = (int(x * view.scale), int(y * view.scale))
            color = MARKER_COLORS[i % len(MARKER_COLORS)]
            cv2.drawMarker(canvas, at, color, cv2.MARKER_CROSS, 24, 2)
            cv2.putText(canvas, str(i + 1), (at[0] + 8, at[1] - 8), 0, 0.8, color, 2)
        status = f"pairs: {len(self.pairs())}  next: {self.next_window()}   u=undo r=reset Enter=done q=quit"
        cv2.putText(canvas, status, (10, 30), 0, 0.8, (0, 0, 0), 4)
        cv2.putText(canvas, status, (10, 30), 0, 0.8, (255, 255, 255), 2)
        if view.cursor:
            draw_zoom_box(canvas, view.image, view.cursor)
        return canvas


def draw_zoom_box(canvas, image, cursor):
    """Drawn in the corner opposite the cursor so it never hides the spot being clicked."""
    x, y = cursor
    h, w = image.shape[:2]
    x0, y0 = max(0, x - ZOOM_HALF_SIZE), max(0, y - ZOOM_HALF_SIZE)
    x1, y1 = min(w, x + ZOOM_HALF_SIZE), min(h, y + ZOOM_HALF_SIZE)
    if x1 <= x0 or y1 <= y0:
        return
    zoomed = cv2.resize(image[y0:y1, x0:x1], (ZOOM_BOX_SIZE, ZOOM_BOX_SIZE), interpolation=cv2.INTER_NEAREST)
    middle = ZOOM_BOX_SIZE // 2
    cv2.line(zoomed, (middle, 0), (middle, ZOOM_BOX_SIZE), (0, 0, 255), 1)
    cv2.line(zoomed, (0, middle), (ZOOM_BOX_SIZE, middle), (0, 0, 255), 1)
    box_x = w - ZOOM_BOX_SIZE - 10 if x < w / 2 else 10
    box_y = h - ZOOM_BOX_SIZE - 10 if y < h / 2 else 10
    canvas[box_y:box_y + ZOOM_BOX_SIZE, box_x:box_x + ZOOM_BOX_SIZE] = zoomed
    cv2.rectangle(canvas, (box_x, box_y), (box_x + ZOOM_BOX_SIZE, box_y + ZOOM_BOX_SIZE), (255, 255, 255), 2)


def pick_points(img_photo, img_ref, pairs=None):
    picker = PointPicker(img_photo, img_ref, pairs)
    for name in ("PHOTO", "REF"):
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, 960, 720)
        cv2.setMouseCallback(name, picker.mouse_handler(name))
    try:
        while True:
            for name in ("PHOTO", "REF"):
                cv2.imshow(name, picker.render(name))
            key = cv2.waitKey(30) & 0xFF
            if key in (KEY_ENTER, KEY_RETURN, KEY_SPACE):
                if len(picker.pairs()) >= 4:
                    return picker.pairs()
                logger.info("need at least 4 point pairs")
            elif key == ord("u"):
                picker.undo()
            elif key == ord("r"):
                picker.reset()
            elif key in (KEY_ESC, ord("q")):
                return None
    finally:
        cv2.destroyAllWindows()


def homography_from_pairs(pairs, img_photo, img_ref, refine=True):
    photo_pts = np.float32([p for p, _ in pairs])
    ref_pts = np.float32([r for _, r in pairs])
    if len(pairs) >= 6:
        H, inlier_mask = cv2.findHomography(photo_pts, ref_pts, cv2.RANSAC, CLICK_TOLERANCE_PX)
        off_pairs = [i + 1 for i, ok in enumerate(inlier_mask.ravel()) if not ok]
        if off_pairs:
            logger.info(f"point pairs {off_pairs} disagree with the others and were ignored")
    else:
        H, _ = cv2.findHomography(photo_pts, ref_pts, 0)
    if H is None:
        raise RuntimeError("could not compute a homography from these points")

    if refine:
        cfg = im.MatchConfig()
        for width in (cfg.work_width, 2 * cfg.work_width):
            H, before, after = im.ecc_refine_at_width(H, img_photo, img_ref, width, cfg)
            logger.info(f"ECC refine at {width}px: score {before:.4f} -> {after:.4f}")
    return H / H[2, 2]


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ref", help='reference image (default: the "__" image in P-FixingImg-big)')
    parser.add_argument("--photo", help="photo to align (default: the other image in P-FixingImg-big)")
    parser.add_argument("--out", default=".", help="output folder")
    parser.add_argument("--points", help="saved points json to reuse instead of clicking")
    parser.add_argument("--edit", action="store_true", help="open the picker pre-filled with --points")
    parser.add_argument("--no-refine", action="store_true", help="skip ECC fine-tuning")
    args = parser.parse_args()

    fixing_folder = Path("P-FixingImg-big")
    ref = Path(args.ref or find_reference_image(fixing_folder) or "")
    photo = Path(args.photo or find_image_to_fix(fixing_folder) or "")
    if not ref.is_file() or not photo.is_file():
        logger.error(f"ref '{ref}' or photo '{photo}' not found")
        return
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    img_ref, img_photo = im.read_image(ref), im.read_image(photo)

    pairs = json.loads(Path(args.points).read_text())["pairs"] if args.points else None
    if pairs is None or args.edit:
        pairs = pick_points(img_photo, img_ref, pairs)
        if pairs is None:
            logger.info("cancelled")
            return
        points_path = out_dir / f"__{photo.stem}_points.json"
        saved = {"photo": str(photo.resolve()), "ref": str(ref.resolve()), "pairs": pairs}
        points_path.write_text(json.dumps(saved, indent=1))
        logger.info(f"points saved to {points_path}")

    H = homography_from_pairs(pairs, img_photo, img_ref, refine=not args.no_refine)
    h, w = img_ref.shape[:2]
    aligned = cv2.warpPerspective(img_photo, H, (w, h), flags=cv2.INTER_LANCZOS4)
    out_path = out_dir / f"__{photo.stem}.jpg"
    im.save_with_exif(out_path, aligned, photo)
    im.write_image(out_dir / f"__{photo.stem}_check.jpg", im.make_check_image(aligned, img_ref), quality=90)
    logger.info(f"[{out_path}] created")


if __name__ == "__main__":
    main()
