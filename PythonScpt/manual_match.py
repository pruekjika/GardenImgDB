"""Manual fallback: click matching points in both photos, then warp.

Use when main.py's automatic match is off (check the __<name>_check.jpg).

    python PythonScpt/manual_match.py                 # pick points, then warp
    python PythonScpt/manual_match.py --points p.json # reuse saved points
    python PythonScpt/manual_match.py --no-refine     # skip ECC fine-tuning

Two windows open: "BAD" (photo to fix) and "REF" (reference). Click a spot in
BAD, then the same spot in REF; repeat for at least 4 pairs (6-10 spread over
the whole image is better: road corners, building corners, pond tips).
Windows can be resized/maximised for precision; a zoom box follows the cursor.

Keys:  u = undo last point   r = reset all   Enter/Space = done   Esc/q = quit
Points are saved to <out>/__<name>_points.json so you can tweak and rerun.
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

from Util.me_logger import logger
from Util.folder_util import find_ref_img, find_to_fixed_img
import img_matcher as im

DISPLAY_WIDTH = 1800
ZOOM_SRC = 60  # half-size (display px) of the area shown in the zoom box
ZOOM_OUT = 240  # zoom box size (display px)
COLORS = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 0, 255),
          (255, 255, 0), (0, 128, 255), (255, 128, 0), (128, 0, 255), (0, 255, 128)]


class _Picker:
    def __init__(self, img_bad, img_ref, pairs=None):
        self.views = {}
        for name, img in (("BAD", img_bad), ("REF", img_ref)):
            s = DISPLAY_WIDTH / img.shape[1]
            self.views[name] = {
                "img": cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA),
                "scale": s,
                "pts": [],
                "cursor": None,
            }
        for b, r in pairs or []:
            self.views["BAD"]["pts"].append(tuple(b))
            self.views["REF"]["pts"].append(tuple(r))

    def expected(self):
        """Which window the next click belongs to."""
        nb, nr = len(self.views["BAD"]["pts"]), len(self.views["REF"]["pts"])
        return "BAD" if nb == nr else "REF"

    def on_mouse(self, name):
        def cb(event, x, y, flags, _):
            v = self.views[name]
            v["cursor"] = (x, y)
            if event == cv2.EVENT_LBUTTONDOWN:
                if name != self.expected():
                    logger.info(f"click in {self.expected()} next")
                    return
                v["pts"].append((x / v["scale"], y / v["scale"]))  # store full-res
        return cb

    def undo(self):
        b, r = self.views["BAD"]["pts"], self.views["REF"]["pts"]
        if len(b) > len(r):
            b.pop()
        elif r:
            r.pop()

    def reset(self):
        for v in self.views.values():
            v["pts"].clear()

    def pairs(self):
        b, r = self.views["BAD"]["pts"], self.views["REF"]["pts"]
        n = min(len(b), len(r))
        return [(list(b[i]), list(r[i])) for i in range(n)]

    def render(self, name):
        v = self.views[name]
        canvas = v["img"].copy()
        for i, (x, y) in enumerate(v["pts"]):
            p = (int(x * v["scale"]), int(y * v["scale"]))
            c = COLORS[i % len(COLORS)]
            cv2.drawMarker(canvas, p, c, cv2.MARKER_CROSS, 24, 2)
            cv2.putText(canvas, str(i + 1), (p[0] + 8, p[1] - 8), 0, 0.8, c, 2)
        msg = f"pairs: {len(self.pairs())}  next: {self.expected()}   u=undo r=reset Enter=done q=quit"
        cv2.putText(canvas, msg, (10, 30), 0, 0.8, (0, 0, 0), 4)
        cv2.putText(canvas, msg, (10, 30), 0, 0.8, (255, 255, 255), 2)
        if v["cursor"]:
            self._draw_zoom(canvas, v["img"], v["cursor"])
        return canvas

    @staticmethod
    def _draw_zoom(canvas, src, cursor):
        x, y = cursor
        h, w = src.shape[:2]
        x0, y0 = max(0, x - ZOOM_SRC), max(0, y - ZOOM_SRC)
        x1, y1 = min(w, x + ZOOM_SRC), min(h, y + ZOOM_SRC)
        if x1 <= x0 or y1 <= y0:
            return
        patch = cv2.resize(src[y0:y1, x0:x1], (ZOOM_OUT, ZOOM_OUT), interpolation=cv2.INTER_NEAREST)
        c = ZOOM_OUT // 2
        cv2.line(patch, (c, 0), (c, ZOOM_OUT), (0, 0, 255), 1)
        cv2.line(patch, (0, c), (ZOOM_OUT, c), (0, 0, 255), 1)
        # put zoom box in the corner away from the cursor
        ox = w - ZOOM_OUT - 10 if x < w / 2 else 10
        oy = h - ZOOM_OUT - 10 if y < h / 2 else 10
        canvas[oy:oy + ZOOM_OUT, ox:ox + ZOOM_OUT] = patch
        cv2.rectangle(canvas, (ox, oy), (ox + ZOOM_OUT, oy + ZOOM_OUT), (255, 255, 255), 2)


def pick_points(img_bad, img_ref, pairs=None):
    picker = _Picker(img_bad, img_ref, pairs)
    for name in ("BAD", "REF"):
        cv2.namedWindow(name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(name, 960, 720)
        cv2.setMouseCallback(name, picker.on_mouse(name))
    try:
        while True:
            for name in ("BAD", "REF"):
                cv2.imshow(name, picker.render(name))
            key = cv2.waitKey(30) & 0xFF
            if key in (13, 10, 32):  # Enter / Space
                if len(picker.pairs()) >= 4:
                    return picker.pairs()
                logger.info("need at least 4 point pairs")
            elif key == ord("u"):
                picker.undo()
            elif key == ord("r"):
                picker.reset()
            elif key in (27, ord("q")):
                return None
    finally:
        cv2.destroyAllWindows()


def homography_from_pairs(pairs, img_bad, img_ref, refine=True):
    pb = np.float32([p[0] for p in pairs])
    pr = np.float32([p[1] for p in pairs])
    if len(pairs) >= 6:
        # full-res px: one display px is ~4 px on an 8064-wide photo, so allow slack
        H, mask = cv2.findHomography(pb, pr, cv2.RANSAC, 40.0)
        bad = [i + 1 for i, m in enumerate(mask.ravel()) if not m]
        if bad:
            logger.info(f"point pairs {bad} look inconsistent with the others (ignored)")
    else:
        H, _ = cv2.findHomography(pb, pr, 0)
    if H is None:
        raise RuntimeError("could not compute a homography from these points")

    if refine:
        cfg = im.MatchConfig()
        for width in (cfg.work_width, 2 * cfg.work_width):  # coarse then fine
            H, before, after = im.refine_ecc(H, img_bad, img_ref, width, cfg)
            logger.info(f"ECC refine @{width}px score {before:.4f} -> {after:.4f}")
    return H / H[2, 2]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ref", help="reference image (default: __* file in P-FixingImg-big)")
    ap.add_argument("--bad", help="image to fix (default: other image in P-FixingImg-big)")
    ap.add_argument("--out", default=".", help="output folder (default: current folder)")
    ap.add_argument("--points", help="json of saved point pairs; skips (or pre-fills with --edit) clicking")
    ap.add_argument("--edit", action="store_true", help="open picker pre-filled with --points")
    ap.add_argument("--no-refine", action="store_true", help="skip ECC fine-tuning")
    args = ap.parse_args()

    folder = Path("P-FixingImg-big").resolve()
    ref = Path(args.ref or find_ref_img(folder) or "")
    bad = Path(args.bad or find_to_fixed_img(folder) or "")
    if not ref.is_file() or not bad.is_file():
        logger.error(f"ref:{ref} / bad:{bad} not found")
        return
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    points_path = out_dir / f"__{bad.stem}_points.json"

    img_ref, img_bad = im.read_image(ref), im.read_image(bad)

    pairs = None
    if args.points:
        pairs = json.loads(Path(args.points).read_text())["pairs"]
    if pairs is None or args.edit:
        pairs = pick_points(img_bad, img_ref, pairs)
        if pairs is None:
            logger.info("cancelled")
            return
        points_path.write_text(json.dumps({"bad": str(bad), "ref": str(ref), "pairs": pairs}, indent=1))
        logger.info(f"points saved to {points_path}")

    H = homography_from_pairs(pairs, img_bad, img_ref, refine=not args.no_refine)
    h, w = img_ref.shape[:2]
    fixed = cv2.warpPerspective(img_bad, H, (w, h), flags=cv2.INTER_LANCZOS4)

    out_path = out_dir / f"__{bad.stem}.jpg"
    im._write_jpg_with_exif(out_path, fixed, bad)
    check_path = out_dir / f"__{bad.stem}_check.jpg"
    im.write_image(check_path, im.make_check_image(fixed, img_ref), quality=90)
    logger.info(f"[{out_path}] created, check: {check_path}")


if __name__ == "__main__":
    main()
