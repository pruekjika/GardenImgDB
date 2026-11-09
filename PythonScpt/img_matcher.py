"""Align one drone photo onto a reference photo.

Photos are taken months apart (dry vs. green season, different shadows), so
matching is done on downscaled, contrast-normalised copies:
  coarse  - SIFT matched only near the same position (the drone flies from the
            same spot), fitted as a similarity; global matching as a fallback
  refine  - match again in a tight radius around the coarse fit -> homography
  ecc     - fine-tune on edge maps, which survive season changes better than colour
The best-scoring plausible stage wins.
"""

from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from Util.me_logger import logger

JPG_QUALITY = 95
WEBP_QUALITY = 50  # same file size as the File Converter webp files already in ImageDB


@dataclass
class MatchConfig:
    work_width: int = 1600
    max_features: int = 20000
    search_radius_fraction: float = 0.15
    refine_radius_px: int = 25
    ecc_iterations: int = 200
    ecc_hires_width: int = 0
    max_scale_change: float = 2.0
    max_rotation_deg: float = 45.0


@dataclass
class MatchResult:
    photo_to_ref: np.ndarray
    stage: str
    score: float
    inliers: int


@dataclass
class PreparedImage:
    gray: np.ndarray
    edges: np.ndarray
    content_mask: np.ndarray
    scale: float


@dataclass
class Keypoints:
    points: np.ndarray
    descriptors: np.ndarray


def read_image(path):
    img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"cannot read image: {path}")
    return img


def write_image(path, img, quality=95):
    ok, encoded = cv2.imencode(Path(path).suffix or ".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, quality])
    if not ok:
        raise IOError(f"cannot encode image: {path}")
    encoded.tofile(str(path))


def save_with_metadata(out_path, img_bgr, metadata_source, quality=None):
    """Saves .jpg or .webp with the source photo's EXIF and XMP (drone date, GPS, gimbal)."""
    is_webp = Path(out_path).suffix.lower() == ".webp"
    options = {"quality": quality or (WEBP_QUALITY if is_webp else JPG_QUALITY)}
    if is_webp:
        options["method"] = 6
    with Image.open(metadata_source) as source:
        for key in ("exif", "xmp"):
            if source.info.get(key):
                options[key] = source.info[key]
    if "exif" not in options:
        logger.info(f"no EXIF in {metadata_source}, saved without it")
    Image.fromarray(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)).save(out_path, "WEBP" if is_webp else "JPEG", **options)


def make_check_image(aligned, ref, width=2400, tiles=8):
    """Left half: 50/50 blend. Right half: checkerboard, where misalignment shows as broken edges."""
    scale = width / 2 / ref.shape[1]
    a = cv2.resize(aligned, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    b = cv2.resize(ref, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    h, w = a.shape[:2]
    rows, cols = np.mgrid[0:h, 0:w]
    is_a_tile = ((rows * tiles // h + cols * tiles // w) % 2 == 0)[..., None]
    return np.hstack([cv2.addWeighted(a, 0.5, b, 0.5, 0), np.where(is_a_tile, a, b)])


def prepare(img, width):
    """content_mask excludes black borders: a ref that is itself a warped photo
    has black corners whose hard edge would attract features and pull the fit."""
    scale = width / img.shape[1]
    small = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    content_mask = cv2.erode((small.max(axis=2) > 8).astype(np.uint8) * 255, np.ones((15, 15), np.uint8))
    gray = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY))
    blurred = cv2.GaussianBlur(gray, (0, 0), 2).astype(np.float32)
    edges = cv2.magnitude(cv2.Sobel(blurred, cv2.CV_32F, 1, 0), cv2.Sobel(blurred, cv2.CV_32F, 0, 1))
    edges *= content_mask > 0
    return PreparedImage(gray, edges / (edges.max() + 1e-6), content_mask, scale)


def detect_keypoints(prepared: PreparedImage, max_features):
    found, descriptors = cv2.SIFT_create(max_features).detectAndCompute(prepared.gray, prepared.content_mask)
    if descriptors is None:
        descriptors = np.zeros((0, 128), np.float32)
    root_sift = np.sqrt(descriptors / (descriptors.sum(axis=1, keepdims=True) + 1e-7))
    return Keypoints(np.float32([k.pt for k in found]).reshape(-1, 2), root_sift.astype(np.float32))


def work_to_full(H, photo_scale, ref_scale):
    return np.diag([1 / ref_scale, 1 / ref_scale, 1]) @ H @ np.diag([photo_scale, photo_scale, 1])


def full_to_work(H, photo_scale, ref_scale):
    return np.diag([ref_scale, ref_scale, 1]) @ H @ np.diag([1 / photo_scale, 1 / photo_scale, 1])


def match_near(photo: Keypoints, ref: Keypoints, predicted_points, ref_shape, radius, ratio, tiles=8):
    """Match each photo keypoint only to ref keypoints within `radius` of where it is predicted to land."""
    matcher = cv2.BFMatcher(cv2.NORM_L2)
    h, w = ref_shape
    tile_h, tile_w = h / tiles, w / tiles
    matches = []
    for ty in range(tiles):
        for tx in range(tiles):
            x0, x1, y0, y1 = tx * tile_w, (tx + 1) * tile_w, ty * tile_h, (ty + 1) * tile_h
            photo_idx = np.where(
                (predicted_points[:, 0] >= x0) & (predicted_points[:, 0] < x1)
                & (predicted_points[:, 1] >= y0) & (predicted_points[:, 1] < y1)
            )[0]
            ref_idx = np.where(
                (ref.points[:, 0] >= x0 - radius) & (ref.points[:, 0] < x1 + radius)
                & (ref.points[:, 1] >= y0 - radius) & (ref.points[:, 1] < y1 + radius)
            )[0]
            if len(photo_idx) == 0 or len(ref_idx) < 2:
                continue
            distance = np.linalg.norm(predicted_points[photo_idx][:, None] - ref.points[ref_idx][None], axis=2)
            within_radius = (distance < radius).astype(np.uint8)
            for best in matcher.knnMatch(photo.descriptors[photo_idx], ref.descriptors[ref_idx], k=2, mask=within_radius):
                if len(best) == 1 or (len(best) == 2 and best[0].distance < ratio * best[1].distance):
                    matches.append((photo_idx[best[0].queryIdx], ref_idx[best[0].trainIdx], best[0].distance))
    return keep_best_match_per_ref_point(photo, ref, matches)


def match_anywhere(photo: Keypoints, ref: Keypoints, ratio=0.8):
    matches = []
    for best in cv2.BFMatcher(cv2.NORM_L2).knnMatch(photo.descriptors, ref.descriptors, k=2):
        if len(best) == 2 and best[0].distance < ratio * best[1].distance:
            matches.append((best[0].queryIdx, best[0].trainIdx, best[0].distance))
    return keep_best_match_per_ref_point(photo, ref, matches)


def keep_best_match_per_ref_point(photo: Keypoints, ref: Keypoints, matches):
    """Many photo points on one ref point let RANSAC accept a degenerate zero-scale fit."""
    if not matches:
        return np.zeros((0, 2), np.float32), np.zeros((0, 2), np.float32)
    matches = np.array(matches)
    matches = matches[np.argsort(matches[:, 2])]
    _, first_per_ref = np.unique(matches[:, 1], return_index=True)
    matches = matches[np.sort(first_per_ref)].astype(int)
    return photo.points[matches[:, 0]], ref.points[matches[:, 1]]


def fit_similarity(photo_pts, ref_pts):
    if len(photo_pts) < 4:
        return None, 0
    A, inlier_mask = cv2.estimateAffinePartial2D(
        photo_pts, ref_pts, method=cv2.RANSAC, ransacReprojThreshold=6.0, maxIters=20000, confidence=0.999
    )
    if A is None:
        return None, 0
    return np.vstack([A, [0, 0, 1]]), int(inlier_mask.sum())


def fit_homography(photo_pts, ref_pts):
    """Returns (H, inlier_mask) or (None, None)."""
    if len(photo_pts) < 8:
        return None, None
    H, inlier_mask = cv2.findHomography(photo_pts, ref_pts, cv2.USAC_MAGSAC, 3.0, maxIters=20000, confidence=0.9999)
    if H is None:
        return None, None
    return H, inlier_mask.ravel().astype(bool)


def is_plausible(H, photo_shape, ref_shape, cfg: MatchConfig, max_rotation_deg=None):
    """Rejects flips, twisted corners, huge zoom, a photo landing off the ref, and too much rotation."""
    if H is None or not np.all(np.isfinite(H)):
        return False
    h, w = photo_shape[:2]
    corners = cv2.perspectiveTransform(np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2), H).reshape(-1, 2)
    if not cv2.isContourConvex(corners.astype(np.float32)):
        return False
    area_ratio = cv2.contourArea(corners) / float(w * h)
    if not (1 / cfg.max_scale_change**2 < area_ratio < cfg.max_scale_change**2):
        return False
    ref_h, ref_w = ref_shape[:2]
    center_x, center_y = corners.mean(axis=0)
    if not (-0.25 * ref_w < center_x < 1.25 * ref_w and -0.25 * ref_h < center_y < 1.25 * ref_h):
        return False
    if max_rotation_deg is not None:
        top_edge = corners[1] - corners[0]
        if abs(np.degrees(np.arctan2(top_edge[1], top_edge[0]))) > max_rotation_deg:
            return False
    return True


def edge_similarity(H, photo_edges, ref_edges):
    """Correlation of edge maps where the warped photo overlaps the ref, -1..1."""
    size = (ref_edges.shape[1], ref_edges.shape[0])
    warped = cv2.warpPerspective(photo_edges, H, size)
    overlap = cv2.warpPerspective(np.ones_like(photo_edges), H, size) > 0.5
    if overlap.sum() < 0.2 * overlap.size:
        return -1.0
    a, b = warped[overlap], ref_edges[overlap]
    a, b = a - a.mean(), b - b.mean()
    return float((a * b).sum() / (np.sqrt((a * a).sum() * (b * b).sum()) + 1e-9))


def ecc_refine(H, photo_edges, ref_edges, iterations):
    """findTransformECC maps ref -> photo, hence the inversions."""
    ref_to_photo = np.linalg.inv(H).astype(np.float32)
    ref_to_photo /= ref_to_photo[2, 2]
    criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, iterations, 1e-6)
    _, ref_to_photo = cv2.findTransformECC(ref_edges, photo_edges, ref_to_photo, cv2.MOTION_HOMOGRAPHY, criteria, None, 5)
    refined = np.linalg.inv(ref_to_photo)
    return refined / refined[2, 2]


def ecc_refine_at_width(photo_to_ref, img_photo, img_ref, width, cfg: MatchConfig):
    """Returns (photo_to_ref, score_before, score_after); keeps the input unless the score improves."""
    photo, ref = prepare(img_photo, width), prepare(img_ref, width)
    H = full_to_work(photo_to_ref, photo.scale, ref.scale)
    before = edge_similarity(H, photo.edges, ref.edges)
    try:
        refined = ecc_refine(H, photo.edges, ref.edges, cfg.ecc_iterations)
    except cv2.error:
        return photo_to_ref, before, before
    after = edge_similarity(refined, photo.edges, ref.edges)
    if after > before and is_plausible(refined, photo.gray.shape, ref.gray.shape, cfg):
        return work_to_full(refined, photo.scale, ref.scale), before, after
    return photo_to_ref, before, after


def estimate_alignment(img_photo, img_ref, cfg: MatchConfig = None) -> MatchResult:
    cfg = cfg or MatchConfig()
    photo, ref = prepare(img_photo, cfg.work_width), prepare(img_ref, cfg.work_width)
    photo_kp, ref_kp = detect_keypoints(photo, cfg.max_features), detect_keypoints(ref, cfg.max_features)
    logger.info(f"keypoints photo={len(photo_kp.points)} ref={len(ref_kp.points)} (work width {cfg.work_width})")

    candidates = []

    def consider(stage, H, inliers, max_rotation_deg=None):
        if H is None:
            logger.info(f"[{stage}] no transform")
        elif not is_plausible(H, photo.gray.shape, ref.gray.shape, cfg, max_rotation_deg):
            logger.info(f"[{stage}] rejected as implausible, inliers={inliers}")
        else:
            score = edge_similarity(H, photo.edges, ref.edges)
            logger.info(f"[{stage}] inliers={inliers} score={score:.4f}")
            candidates.append(MatchResult(H, stage, score, inliers))

    def best():
        return max(candidates, key=lambda c: c.score)

    photo_pts, ref_pts = match_near(
        photo_kp, ref_kp, photo_kp.points, ref.gray.shape, cfg.search_radius_fraction * cfg.work_width, ratio=0.85
    )
    consider("coarse-near", *fit_similarity(photo_pts, ref_pts), cfg.max_rotation_deg)
    if not candidates:
        consider("coarse-anywhere", *fit_similarity(*match_anywhere(photo_kp, ref_kp)))
    if not candidates:
        raise RuntimeError("automatic matching failed - use manual_match.py to pick point pairs by hand")

    predicted = cv2.perspectiveTransform(photo_kp.points.reshape(-1, 1, 2), best().photo_to_ref).reshape(-1, 2)
    photo_pts, ref_pts = match_near(photo_kp, ref_kp, predicted, ref.gray.shape, cfg.refine_radius_px, ratio=0.9)
    H, inlier_mask = fit_homography(photo_pts, ref_pts)
    consider("refine", H, 0 if inlier_mask is None else int(inlier_mask.sum()))

    try:
        consider("ecc", ecc_refine(best().photo_to_ref, photo.edges, ref.edges, cfg.ecc_iterations), best().inliers)
    except cv2.error:
        logger.info("[ecc] did not converge")

    result = best()
    result.photo_to_ref = work_to_full(result.photo_to_ref, photo.scale, ref.scale)
    if cfg.ecc_hires_width > cfg.work_width:
        refined, before, after = ecc_refine_at_width(result.photo_to_ref, img_photo, img_ref, cfg.ecc_hires_width, cfg)
        logger.info(f"[ecc-hires] score {before:.4f} -> {after:.4f} (width {cfg.ecc_hires_width})")
        if refined is not result.photo_to_ref:
            result = MatchResult(refined, "ecc-hires", after, result.inliers)

    result.photo_to_ref = result.photo_to_ref / result.photo_to_ref[2, 2]
    logger.info(f"chosen stage: {result.stage} (score {result.score:.4f})")
    return result


def create_fix_image(ref_path, photo_path, out_dir, cfg: MatchConfig = None, prefix="__"):
    """Writes <out_dir>/<prefix><photo>.jpg (with the photo's metadata) and <prefix><photo>_check.jpg.
    Returns (MatchResult, aligned image)."""
    ref_path, photo_path, out_dir = Path(ref_path), Path(photo_path), Path(out_dir)
    logger.info(f"aligning '{photo_path.name}' onto ref '{ref_path.name}'")
    img_ref, img_photo = read_image(ref_path), read_image(photo_path)
    result = estimate_alignment(img_photo, img_ref, cfg)

    h, w = img_ref.shape[:2]
    aligned = cv2.warpPerspective(img_photo, result.photo_to_ref, (w, h), flags=cv2.INTER_LANCZOS4)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{prefix}{photo_path.stem}.jpg"
    save_with_metadata(out_path, aligned, photo_path)
    check_path = out_dir / f"{prefix}{photo_path.stem}_check.jpg"
    write_image(check_path, make_check_image(aligned, img_ref), quality=90)
    logger.info(f"[{out_path}] created, check: {check_path.name}")
    return result, aligned
