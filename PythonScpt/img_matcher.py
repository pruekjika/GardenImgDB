"""Align a new drone photo ("bad") onto a reference photo ("ref").

Why the old ORB pipeline failed: the two photos are taken months apart
(dry season vs. green season, different sun/shadows, different resolution),
so most raw descriptor matches are wrong. Keeping the "top 0.5%" by distance
still left mostly outliers and RANSAC returned a garbage homography.

New pipeline (all on downscaled, contrast-normalised copies, then scaled back):

1. coarse   - RootSIFT + *guided* matching: the drone is flown from the same spot
              at the same height, so a point in "bad" is searched for only near
              the same relative position in "ref". Fit a similarity transform
              (scale + rotation + shift), which needs very few correct matches.
              Falls back to un-guided global matching if that fails.
2. refine   - Warp keypoints with the coarse transform and match again inside a
              tight radius -> many more correct matches -> full homography.
3. ecc      - Intensity refinement (findTransformECC) on gradient-magnitude
              images, which follow edges (roads, ponds, field borders) rather
              than colour, so season changes matter less.

Every stage is scored (edge correlation in the overlap) and sanity-checked;
the best valid result wins. A blend/checkerboard "check" image is written next
to the output so a bad alignment is obvious at a glance. If automatic matching
still fails, use manual_match.py to click point pairs by hand.
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from Util.me_logger import logger


@dataclass
class MatchConfig:
    work_width: int = 1600  # both images are resized to this width for matching
    max_features: int = 20000
    search_radius: float = 0.15  # guided search radius, fraction of work_width
    refine_radius_px: int = 25  # tight radius (work px) for the refine stage
    ecc_iters: int = 200
    ecc_full_width: int = 0  # >0: extra ECC pass at this width (slower, finer)
    max_scale_change: float = 2.0  # reject transforms that scale more than this
    max_rotation_deg: float = 45.0  # for the guided (same-spot) coarse stage


@dataclass
class MatchResult:
    homography: np.ndarray  # maps full-res bad pixels -> full-res ref pixels
    stage: str
    score: float
    inliers: int


# ---------------------------------------------------------------- image utils
def read_image(path):
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"cannot read image: {path}")
    return img


def write_image(path, img, quality=95):
    ext = Path(path).suffix or ".jpg"
    ok, buf = cv2.imencode(ext, img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise IOError(f"cannot encode image: {path}")
    buf.tofile(str(path))


def _prep(img, width):
    """Resize to `width`, grayscale, CLAHE.
    Returns (gray, edges, valid, scale). `valid` (uint8 0/255) excludes black
    borders: a reference that is itself a warped photo has black corners whose
    hard edge would otherwise attract features and pull the ECC fit."""
    s = width / img.shape[1]
    small = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    valid = cv2.erode((small.max(axis=2) > 8).astype(np.uint8) * 255, np.ones((15, 15), np.uint8))
    gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)
    g = cv2.GaussianBlur(gray, (0, 0), 2).astype(np.float32)
    edges = cv2.magnitude(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))
    edges *= valid > 0
    return gray, edges / (edges.max() + 1e-6), valid, s


def _scale_h(H, s_bad, s_ref):
    """Convert a homography between scaled images into one between the originals."""
    return np.diag([1 / s_ref, 1 / s_ref, 1]) @ H @ np.diag([s_bad, s_bad, 1])


# --------------------------------------------------------------- matching
class _Features:
    def __init__(self, gray, valid, n):
        kp, des = cv2.SIFT_create(n).detectAndCompute(gray, valid)
        self.pts = np.float32([k.pt for k in kp]).reshape(-1, 2)
        if des is None:
            des = np.zeros((0, 128), np.float32)
        des = des / (des.sum(axis=1, keepdims=True) + 1e-7)  # RootSIFT
        self.des = np.sqrt(des).astype(np.float32)


def _guided_matches(fb, fr, bad_pts, shape, radius, ratio, tiles=8):
    """Match each bad keypoint only to ref keypoints within `radius` of
    `bad_pts` (bad keypoints already mapped into ref coordinates)."""
    bf = cv2.BFMatcher(cv2.NORM_L2)
    h, w = shape
    th, tw = h / tiles, w / tiles
    pairs = []
    for ty in range(tiles):
        for tx in range(tiles):
            x0, x1, y0, y1 = tx * tw, (tx + 1) * tw, ty * th, (ty + 1) * th
            qi = np.where(
                (bad_pts[:, 0] >= x0) & (bad_pts[:, 0] < x1)
                & (bad_pts[:, 1] >= y0) & (bad_pts[:, 1] < y1)
            )[0]
            ti = np.where(
                (fr.pts[:, 0] >= x0 - radius) & (fr.pts[:, 0] < x1 + radius)
                & (fr.pts[:, 1] >= y0 - radius) & (fr.pts[:, 1] < y1 + radius)
            )[0]
            if len(qi) == 0 or len(ti) < 2:
                continue
            dist = np.linalg.norm(bad_pts[qi][:, None] - fr.pts[ti][None], axis=2)
            mask = (dist < radius).astype(np.uint8)
            for m in bf.knnMatch(fb.des[qi], fr.des[ti], k=2, mask=mask):
                if len(m) == 2 and m[0].distance < ratio * m[1].distance:
                    pairs.append((qi[m[0].queryIdx], ti[m[0].trainIdx]))
                elif len(m) == 1:
                    pairs.append((qi[m[0].queryIdx], ti[m[0].trainIdx]))
    if not pairs:
        return np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32)
    pairs = np.array(pairs)
    return fb.pts[pairs[:, 0]], fr.pts[pairs[:, 1]]


def _global_matches(fb, fr, ratio=0.8):
    good = []
    for m in cv2.BFMatcher(cv2.NORM_L2).knnMatch(fb.des, fr.des, k=2):
        if len(m) == 2 and m[0].distance < ratio * m[1].distance:
            good.append((m[0].queryIdx, m[0].trainIdx))
    if not good:
        return np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32)
    good = np.array(good)
    return fb.pts[good[:, 0]], fr.pts[good[:, 1]]


def _fit_similarity(pb, pr, thresh=6.0):
    if len(pb) < 4:
        return None, 0
    A, mask = cv2.estimateAffinePartial2D(
        pb, pr, method=cv2.RANSAC, ransacReprojThreshold=thresh,
        maxIters=20000, confidence=0.999,
    )
    if A is None:
        return None, 0
    return np.vstack([A, [0, 0, 1]]), int(mask.sum())


def _fit_homography(pb, pr, thresh=3.0):
    if len(pb) < 8:
        return None, 0
    H, mask = cv2.findHomography(pb, pr, cv2.USAC_MAGSAC, thresh, maxIters=20000, confidence=0.9999)
    if H is None:
        return None, 0
    return H, int(mask.sum())


# --------------------------------------------------------------- validation
def _is_sane(H, bad_shape, ref_shape, cfg, max_rot=None):
    """Reject degenerate homographies (flips, huge zoom, twisted corners)."""
    if H is None or not np.all(np.isfinite(H)):
        return False
    h, w = bad_shape[:2]
    corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    c = cv2.perspectiveTransform(corners, H).reshape(-1, 2)
    if not cv2.isContourConvex(c.astype(np.float32)):
        return False
    area_ratio = cv2.contourArea(c) / float(w * h)
    lo, hi = 1 / cfg.max_scale_change**2, cfg.max_scale_change**2
    if not (lo < area_ratio < hi):
        return False
    # the warped image must overlap the reference a good amount
    rh, rw = ref_shape[:2]
    cx, cy = c.mean(axis=0)
    if not (-0.25 * rw < cx < 1.25 * rw and -0.25 * rh < cy < 1.25 * rh):
        return False
    if max_rot is not None:
        top = c[1] - c[0]
        rot = np.degrees(np.arctan2(top[1], top[0]))
        if abs(rot) > max_rot:
            return False
    return True


def _score(H, gb_grad, gr_grad):
    """Normalised correlation of edge maps in the overlap region (-1..1)."""
    size = (gr_grad.shape[1], gr_grad.shape[0])
    warped = cv2.warpPerspective(gb_grad, H, size)
    valid = cv2.warpPerspective(np.ones_like(gb_grad), H, size) > 0.5
    if valid.sum() < 0.2 * valid.size:
        return -1.0
    a, b = warped[valid], gr_grad[valid]
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))


def _ecc(H_init, gb_grad, gr_grad, iters):
    """ECC maps template(ref) -> input(bad), so invert in and out."""
    warp = np.linalg.inv(H_init).astype(np.float32)
    warp /= warp[2, 2]
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iters, 1e-6)
    _, warp = cv2.findTransformECC(gr_grad, gb_grad, warp, cv2.MOTION_HOMOGRAPHY, criteria, None, 5)
    H = np.linalg.inv(warp)
    return H / H[2, 2]


def refine_ecc(H_full, img_bad, img_ref, width, cfg: MatchConfig):
    """ECC-refine a full-res homography at `width`. Keeps the input unless the
    edge score improves. Returns (H_full, score_before, score_after)."""
    gb, eb, _, sb = _prep(img_bad, width)
    gr, er, _, sr = _prep(img_ref, width)
    H = np.diag([sr, sr, 1]) @ H_full @ np.diag([1 / sb, 1 / sb, 1])
    before = _score(H, eb, er)
    try:
        H2 = _ecc(H, eb, er, cfg.ecc_iters)
    except cv2.error:
        return H_full, before, before
    after = _score(H2, eb, er)
    if after > before and _is_sane(H2, gb.shape, gr.shape, cfg):
        return _scale_h(H2, sb, sr), before, after
    return H_full, before, after


# --------------------------------------------------------------- main API
def estimate_alignment(img_bad, img_ref, cfg: MatchConfig = None) -> MatchResult:
    cfg = cfg or MatchConfig()
    note = logger.info

    gb, gb_grad, vb, sb = _prep(img_bad, cfg.work_width)
    gr, gr_grad, vr, sr = _prep(img_ref, cfg.work_width)
    fb, fr = _Features(gb, vb, cfg.max_features), _Features(gr, vr, cfg.max_features)
    note(f"features bad={len(fb.pts)} ref={len(fr.pts)} (work width {cfg.work_width})")

    candidates = []  # (score, stage, H_work, inliers)

    def consider(stage, H, inliers, max_rot=None):
        if H is None:
            note(f"[{stage}] no transform")
            return
        if not _is_sane(H, gb.shape, gr.shape, cfg, max_rot):
            note(f"[{stage}] rejected (degenerate transform), inliers={inliers}")
            return
        sc = _score(H, gb_grad, gr_grad)
        note(f"[{stage}] inliers={inliers} score={sc:.4f}")
        candidates.append((sc, stage, H, inliers))

    # 1. coarse: guided (same framing assumption), then global fallback
    radius = cfg.search_radius * cfg.work_width
    pb, pr = _guided_matches(fb, fr, fb.pts, gr.shape, radius, ratio=0.85)
    H, n = _fit_similarity(pb, pr)
    note(f"[coarse-guided] candidate matches={len(pb)}")
    consider("coarse-guided", H, n, cfg.max_rotation_deg)

    if not candidates:
        pb, pr = _global_matches(fb, fr)
        note(f"[coarse-global] candidate matches={len(pb)}")
        H, n = _fit_similarity(pb, pr)
        consider("coarse-global", H, n)

    if not candidates:
        raise RuntimeError(
            "automatic matching failed - use manual_match.py to pick point pairs by hand"
        )

    # 2. refine: re-match in a tight radius around the coarse prediction
    H_coarse = max(candidates, key=lambda c: c[0])[2]
    warped_pts = cv2.perspectiveTransform(fb.pts.reshape(-1, 1, 2), H_coarse).reshape(-1, 2)
    pb, pr = _guided_matches(fb, fr, warped_pts, gr.shape, cfg.refine_radius_px, ratio=0.9)
    note(f"[refine] candidate matches={len(pb)}")
    H, n = _fit_homography(pb, pr)
    consider("refine", H, n)

    # 3. ECC on edge maps, starting from the best so far
    best = max(candidates, key=lambda c: c[0])
    try:
        H = _ecc(best[2], gb_grad, gr_grad, cfg.ecc_iters)
        consider("ecc", H, best[3])
    except cv2.error as e:
        note(f"[ecc] did not converge: {e.msg if hasattr(e, 'msg') else e}")

    best = max(candidates, key=lambda c: c[0])
    H_full = _scale_h(best[2], sb, sr)

    # 4. optional extra ECC pass at a higher resolution
    if cfg.ecc_full_width > cfg.work_width:
        H2, before, after = refine_ecc(H_full, img_bad, img_ref, cfg.ecc_full_width, cfg)
        note(f"[ecc-hires] score {before:.4f} -> {after:.4f} (width {cfg.ecc_full_width})")
        if H2 is not H_full:
            H_full, best = H2, (after, "ecc-hires", None, best[3])

    note(f"chosen stage: {best[1]} (score {best[0]:.4f})")
    return MatchResult(H_full / H_full[2, 2], best[1], best[0], best[3])


def make_check_image(warped, ref, width=2400, tiles=8):
    """Left: 50/50 blend. Right: checkerboard (misalignment = broken edges)."""
    s = width / 2 / ref.shape[1]
    a = cv2.resize(warped, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    b = cv2.resize(ref, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
    blend = cv2.addWeighted(a, 0.5, b, 0.5, 0)
    h, w = a.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w]
    checker = ((yy * tiles // h + xx * tiles // w) % 2 == 0)[..., None]
    board = np.where(checker, a, b)
    return np.hstack([blend, board])


def _write_jpg_with_exif(out_path, img_bgr, exif_source, quality=95):
    """Encode once with the source photo's EXIF (date, GPS...) attached."""
    with Image.open(exif_source) as src:
        exif = src.info.get("exif")
    pil = Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB))
    kwargs = {"quality": quality}
    if exif:
        kwargs["exif"] = exif
    else:
        logger.info(f"no EXIF in {exif_source}, saved without metadata")
    pil.save(out_path, "JPEG", **kwargs)


def create_fix_image(
    ref_path,
    bad_path,
    out_dir,
    cfg: MatchConfig = None,
    lead_word="__",
    write_check=True,
):
    """Align `bad_path` onto `ref_path`, write `<out_dir>/<lead_word><bad stem>.jpg`
    (with the bad image's EXIF) and a `..._check.jpg` overlay. Returns MatchResult."""
    ref_path, bad_path, out_dir = Path(ref_path), Path(bad_path), Path(out_dir)
    logger.info(f"fixing: ref '{ref_path.name}' <- bad '{bad_path.name}'")

    img_ref = read_image(ref_path)
    img_bad = read_image(bad_path)
    result = estimate_alignment(img_bad, img_ref, cfg)

    h, w = img_ref.shape[:2]
    fixed = cv2.warpPerspective(img_bad, result.homography, (w, h), flags=cv2.INTER_LANCZOS4)

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{lead_word}{bad_path.stem}.jpg"
    _write_jpg_with_exif(out_path, fixed, bad_path)
    logger.info(f"[{out_path}] created!  stage={result.stage} score={result.score:.4f}")

    if write_check:
        check_path = out_dir / f"{lead_word}{bad_path.stem}_check.jpg"
        write_image(check_path, make_check_image(fixed, img_ref), quality=90)
        logger.info(f"[{check_path}] created (blend | checkerboard)")

    return result
