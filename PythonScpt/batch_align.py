"""Re-align every original photo to one master reference in a single run.

Matching each photo straight to the master is noisy across seasons, and
chaining photo-to-photo piles up errors. So every photo is matched with its
time neighbours and with the master, then all transforms are solved together
(master fixed) so every match agrees at once. Pairs that disagree with the
rest are dropped. Each original is warped once into the master's frame.

Input: originals named in time order (0.jpg, 1.jpg, ...) in --src.
Output: aligned photos, check/ images, report.html (worst first), results.json,
index.json (photo list + dates for the CompareWeb site).
Reruns are fast: keypoints and pair matches are cached in <out>/.cache.

    python PythonScpt/batch_align.py --src P-Originals --ref 95 --out P-Aligned

Fix one photo by hand, then rerun the line above:
    python PythonScpt/manual_match.py --photo P-Originals/40.jpg --ref P-Originals/95.jpg --out P-Aligned
"""

import argparse
import html
import json
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np

import img_matcher as im
from Util.image_index import write_image_index
from Util.me_logger import logger

IMAGE_SUFFIXES = (".jpg", ".jpeg", ".webp", ".png")
KEYPOINT_CACHE_VERSION = 2
PAIR_CACHE_VERSION = 3
MAX_MATCHES_PER_PAIR = 300
HAND_PICKED_WEIGHT = 20.0
SOLVER_UNIT_PX = 1000.0


@dataclass
class Photo:
    path: Path
    keypoints: im.Keypoints
    scale: float
    work_shape: tuple
    cache_key: str


@dataclass
class PhotoPair:
    points_a: np.ndarray
    points_b: np.ndarray
    match_count: float
    weight: float = 1.0
    hand_picked: bool = False


def list_photos(folder):
    files = [p for p in Path(folder).iterdir() if p.suffix.lower() in IMAGE_SUFFIXES and not p.name.startswith("__")]
    return sorted(files, key=lambda p: (0, int(p.stem), "") if p.stem.isdigit() else (1, 0, p.stem))


def file_fingerprint(path):
    stat = Path(path).stat()
    return f"{stat.st_size}-{int(stat.st_mtime)}"


def read_cache(cache_file, cache_key):
    """The cached arrays, or None when missing, unreadable or written for other inputs/settings."""
    try:
        cached = np.load(cache_file)
    except (OSError, ValueError):
        return None
    if "cache_key" not in cached.files or str(cached["cache_key"]) != cache_key:
        return None
    return cached


def load_photo(path, cache_dir, cfg):
    cache_file = cache_dir / f"keypoints_{path.stem}.npz"
    cache_key = f"{KEYPOINT_CACHE_VERSION}-{file_fingerprint(path)}-{cfg.work_width}-{cfg.max_features}"
    cached = read_cache(cache_file, cache_key)
    if cached is not None:
        keypoints = im.Keypoints(cached["points"], cached["descriptors"])
        return Photo(path, keypoints, float(cached["scale"]), tuple(cached["work_shape"]), cache_key)
    prepared = im.prepare(im.read_image(path), cfg.work_width)
    keypoints = im.detect_keypoints(prepared, cfg.max_features)
    np.savez(cache_file, cache_key=cache_key, points=keypoints.points, descriptors=keypoints.descriptors,
             scale=prepared.scale, work_shape=prepared.gray.shape)
    return Photo(path, keypoints, prepared.scale, prepared.gray.shape, cache_key)


def match_photos(a: Photo, b: Photo, cfg, min_inliers):
    """Inlier point pairs in work px, or None if the photos do not match reliably."""
    near_radius = cfg.search_radius_fraction * cfg.work_width
    coarse_attempts = [
        (lambda: im.match_near(a.keypoints, b.keypoints, a.keypoints.points, b.work_shape, near_radius, 0.85),
         cfg.max_rotation_deg),
        (lambda: im.match_anywhere(a.keypoints, b.keypoints), None),
    ]
    for find_matches, max_rotation_deg in coarse_attempts:
        coarse, _ = im.fit_similarity(*find_matches())
        if not im.is_plausible(coarse, a.work_shape, b.work_shape, cfg, max_rotation_deg):
            continue
        predicted = cv2.perspectiveTransform(a.keypoints.points.reshape(-1, 1, 2), coarse).reshape(-1, 2)
        points_a, points_b = im.match_near(a.keypoints, b.keypoints, predicted, b.work_shape, cfg.refine_radius_px, 0.9)
        H, inliers = im.fit_homography(points_a, points_b)
        if im.is_plausible(H, a.work_shape, b.work_shape, cfg) and inliers.sum() >= min_inliers:
            return points_a[inliers], points_b[inliers]
    return None


def load_pair(a: Photo, b: Photo, cache_dir, cfg, min_inliers):
    cache_file = cache_dir / f"pair_{a.path.stem}__{b.path.stem}.npz"
    cache_key = (f"{PAIR_CACHE_VERSION}|{a.cache_key}|{b.cache_key}|{cfg.search_radius_fraction}"
                 f"|{cfg.refine_radius_px}|{min_inliers}")
    cached = read_cache(cache_file, cache_key)
    if cached is not None:
        return (cached["points_a"], cached["points_b"]) if len(cached["points_a"]) else None
    matched = match_photos(a, b, cfg, min_inliers)
    no_points = np.zeros((0, 2), np.float32)
    np.savez(cache_file, cache_key=cache_key,
             points_a=matched[0] if matched else no_points, points_b=matched[1] if matched else no_points)
    return matched


def load_hand_picked_pair(out_dir, photo: Photo, master: Photo):
    points_file = out_dir / f"__{photo.path.stem}_points.json"
    if not points_file.exists():
        return None
    saved = json.loads(points_file.read_text())
    if Path(saved["ref"]).resolve() != master.path.resolve():
        logger.info(f"{points_file.name} was picked against a different ref, ignored")
        return None
    pairs = np.float32(saved["pairs"])
    return PhotoPair(pairs[:, 0] * photo.scale / SOLVER_UNIT_PX, pairs[:, 1] * master.scale / SOLVER_UNIT_PX,
                     match_count=1e9, weight=HAND_PICKED_WEIGHT, hand_picked=True)


def project_with_jacobian(params, points):
    """Applies an 8-parameter homography; also returns d(projection)/d(params)."""
    x, y = points[:, 0], points[:, 1]
    w = params[6] * x + params[7] * y + 1
    u = (params[0] * x + params[1] * y + params[2]) / w
    v = (params[3] * x + params[4] * y + params[5]) / w
    jacobian = np.zeros((len(points), 2, 8))
    jacobian[:, 0, 0], jacobian[:, 0, 1], jacobian[:, 0, 2] = x / w, y / w, 1 / w
    jacobian[:, 1, 3], jacobian[:, 1, 4], jacobian[:, 1, 5] = x / w, y / w, 1 / w
    jacobian[:, 0, 6], jacobian[:, 0, 7] = -u * x / w, -u * y / w
    jacobian[:, 1, 6], jacobian[:, 1, 7] = -v * x / w, -v * y / w
    return np.stack([u, v], 1), jacobian


def homography_to_params(H):
    return (H / H[2, 2]).ravel()[:8].copy()


def params_to_homography(params):
    return np.append(params, 1.0).reshape(3, 3)


def chain_from_master(master, pairs):
    """Starting guess: chain transforms outward from the master along the strongest pairs."""
    to_master = {master: np.eye(3)}
    while True:
        frontier = [(key, pair) for key, pair in pairs.items() if (key[0] in to_master) != (key[1] in to_master)]
        if not frontier:
            break
        (a, b), pair = max(frontier, key=lambda item: item[1].match_count)
        a_to_b, _ = cv2.findHomography(pair.points_a, pair.points_b, 0)
        if a in to_master:
            to_master[b] = to_master[a] @ np.linalg.inv(a_to_b)
        else:
            to_master[a] = to_master[b] @ a_to_b
    return {name: H / H[2, 2] for name, H in to_master.items()}


def solve_all_transforms(master, pairs, start, iterations=15, huber_px=3.0):
    """Gauss-Newton over every photo's homography at once, master fixed, Huber-weighted."""
    free = [name for name in start if name != master]
    slot = {name: 8 * i for i, name in enumerate(free)}
    params = {name: homography_to_params(start[name]) for name in free}
    huber = huber_px / SOLVER_UNIT_PX
    for _ in range(iterations):
        normal = np.eye(8 * len(free)) * 1e-6
        gradient = np.zeros(8 * len(free))
        for (a, b), pair in pairs.items():
            if a not in start or b not in start:
                continue
            sides = []
            projected = []
            for name, points, sign in ((a, pair.points_a, 1), (b, pair.points_b, -1)):
                if name in slot:
                    at, jacobian = project_with_jacobian(params[name], points)
                    sides.append((slot[name], jacobian, sign))
                    projected.append(at)
                else:
                    projected.append(points)
            residual = projected[0] - projected[1]
            distance = np.linalg.norm(residual, axis=1)
            w = np.where(distance < huber, 1.0, huber / np.maximum(distance, 1e-12)) * pair.weight
            for i, jacobian_i, sign_i in sides:
                gradient[i:i + 8] += sign_i * np.einsum("m,mci,mc->i", w, jacobian_i, residual)
                for j, jacobian_j, sign_j in sides:
                    normal[i:i + 8, j:j + 8] += sign_i * sign_j * np.einsum("m,mci,mcj->ij", w, jacobian_i, jacobian_j)
        step = np.linalg.solve(normal, -gradient)
        for name in free:
            params[name] += step[slot[name]:slot[name] + 8]
        if np.abs(step).max() < 1e-7:
            break
    solved = {name: params_to_homography(params[name]) for name in free}
    solved[master] = np.eye(3)
    return solved


def pair_disagreement(to_master, pairs):
    """Median distance (solver units) between where both photos of a pair put the same point."""
    disagreement = {}
    for (a, b), pair in pairs.items():
        if a in to_master and b in to_master:
            at_a = cv2.perspectiveTransform(pair.points_a.reshape(-1, 1, 2), to_master[a]).reshape(-1, 2)
            at_b = cv2.perspectiveTransform(pair.points_b.reshape(-1, 1, 2), to_master[b]).reshape(-1, 2)
            disagreement[(a, b)] = float(np.median(np.linalg.norm(at_a - at_b, axis=1)))
    return disagreement


def solve_dropping_outliers(master, pairs, names, drop_limit):
    """A wrong pair drags its neighbours off too, so only the worst is dropped per round,
    and never a photo's last pair (that photo is flagged in the report instead)."""
    dropped = []
    while True:
        to_master = solve_all_transforms(master, pairs, chain_from_master(master, pairs))
        disagreement = pair_disagreement(to_master, pairs)
        pair_count = {name: sum(name in key for key in pairs) for name in names}
        droppable = [key for key, d in disagreement.items()
                     if d > drop_limit and not pairs[key].hand_picked and min(pair_count[key[0]], pair_count[key[1]]) > 1]
        if not droppable:
            return to_master, disagreement, dropped
        worst = max(droppable, key=disagreement.get)
        dropped.append((worst, disagreement[worst]))
        pairs.pop(worst)


def write_report(out_dir, rows, master, warn_px):
    lines = []
    for row in sorted(rows, key=lambda r: -1e9 if r["residual_px"] is None else -r["residual_px"]):
        residual = "-" if row["residual_px"] is None else f"{row['residual_px']:.1f}"
        needs_check = row["status"] != "ok" or (row["residual_px"] or 0) > warn_px or len(row["matched_with"]) < 2
        matched_with = ", ".join(f"{name} ({px:.1f})" for name, px in sorted(row["matched_with"], key=lambda t: -t[1]))
        check = f'check/{row["photo"]}.jpg'
        image = f'<a href="{check}"><img src="{check}" loading="lazy"></a>' if row["status"] == "ok" else ""
        label = html.escape(row["photo"]) + (" (master)" if row["photo"] == master else "")
        lines.append(
            f'<tr class="{"warn" if needs_check else ""}"><td>{label}</td><td>{html.escape(row["status"])}</td>'
            f"<td>{residual}</td><td>{html.escape(matched_with)}</td><td>{image}</td></tr>"
        )
    (out_dir / "report.html").write_text(
        "<!doctype html><meta charset=utf-8><title>Alignment report</title><style>"
        "body{font-family:sans-serif;margin:16px;background:#fff;color:#111}"
        "table{border-collapse:collapse}td,th{border:1px solid #ccc;padding:4px 8px;vertical-align:top}"
        "tr.warn{background:#fde8e8}img{width:640px}</style>"
        "<h1>Alignment report</h1><p>Worst first. Residual = median disagreement in output px between this "
        "photo and the photos it was matched with. Red rows need a look; fix with manual_match.py.</p>"
        "<table><tr><th>photo</th><th>status</th><th>residual px</th><th>matched with (px)</th>"
        "<th>blend | checkerboard vs master</th></tr>" + "".join(lines) + "</table>",
        encoding="utf-8",
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--src", default="P-Originals", help="folder of original photos")
    parser.add_argument("--ref", required=True, help="master reference: file name or number inside --src")
    parser.add_argument("--out", default="P-Aligned", help="output folder")
    parser.add_argument("--width", type=int, default=4096, help="output width; height keeps the master's aspect")
    parser.add_argument("--format", choices=("jpg", "webp"), default="jpg")
    parser.add_argument("--quality", type=int, help="default: 95 for jpg, 50 for webp (same as ImageDB)")
    parser.add_argument("--neighbors", type=int, default=3, help="how many following photos each photo is matched with")
    parser.add_argument("--min-inliers", type=int, default=25, help="matches needed to trust a pair")
    parser.add_argument("--drop-px", type=float, default=8.0, help="drop pairs disagreeing more than this (output px)")
    parser.add_argument("--rerender", action="store_true", help="rewrite every output, not only changed ones")
    args = parser.parse_args()

    cfg = im.MatchConfig(work_width=2048)
    out_dir = Path(args.out)
    cache_dir, check_dir = out_dir / ".cache", out_dir / "check"
    for folder in (out_dir, cache_dir, check_dir):
        folder.mkdir(parents=True, exist_ok=True)

    paths = {p.stem: p for p in list_photos(args.src)}
    master = next((name for name, p in paths.items() if args.ref in (name, p.name)), None)
    if master is None:
        raise SystemExit(f"--ref {args.ref} not found in {args.src}")
    names = list(paths)
    logger.info(f"{len(names)} photos, master = {paths[master].name}")

    photos = {}
    for i, name in enumerate(names):
        photos[name] = load_photo(paths[name], cache_dir, cfg)
        print(f"\rkeypoints {i + 1}/{len(names)}", end="", flush=True)
    print()

    wanted = {(a, b) for i, a in enumerate(names) for b in names[i + 1: i + 1 + args.neighbors]}
    wanted |= {(name, master) for name in names if name != master and (master, name) not in wanted}
    pairs = {}
    for i, (a, b) in enumerate(sorted(wanted, key=lambda key: (names.index(key[0]), names.index(key[1])))):
        print(f"\rpairs {i + 1}/{len(wanted)}", end="", flush=True)
        matched = load_pair(photos[a], photos[b], cache_dir, cfg, args.min_inliers)
        if matched is None:
            continue
        points_a, points_b = matched
        if len(points_a) > MAX_MATCHES_PER_PAIR:
            keep = np.random.default_rng(0).choice(len(points_a), MAX_MATCHES_PER_PAIR, replace=False)
            points_a, points_b = points_a[keep], points_b[keep]
        pairs[(a, b)] = PhotoPair(points_a / SOLVER_UNIT_PX, points_b / SOLVER_UNIT_PX, len(matched[0]))
    print()
    for name in names:
        hand_picked = load_hand_picked_pair(out_dir, photos[name], photos[master])
        if hand_picked is not None:
            pairs[(name, master)] = hand_picked
            logger.info(f"{name}: using {len(hand_picked.points_a)} hand-picked points")
    logger.info(f"{len(pairs)} usable pairs out of {len(wanted)} tried")

    work_to_output = args.width / photos[master].work_shape[1]
    solver_to_output_px = SOLVER_UNIT_PX * work_to_output
    to_master, disagreement, dropped = solve_dropping_outliers(master, pairs, names, args.drop_px / solver_to_output_px)
    if dropped:
        logger.info("dropped pairs that disagree with the rest: "
                    + ", ".join(f"{a}-{b} ({d * solver_to_output_px:.0f}px)" for (a, b), d in dropped))

    results_file = out_dir / "results.json"
    previous = json.loads(results_file.read_text()) if results_file.exists() else {}
    out_h, out_w = (np.array(photos[master].work_shape) * work_to_output).round().astype(int)
    master_image = cv2.resize(im.read_image(paths[master]), (out_w, out_h), interpolation=cv2.INTER_AREA)
    rows = []
    for name in names:
        matched_with = [(b if a == name else a, d * solver_to_output_px) for (a, b), d in disagreement.items() if name in (a, b)]
        if name not in to_master:
            rows.append({"photo": name, "status": "FAILED: no pair links it to the master", "residual_px": None, "matched_with": []})
            continue
        photo_scale = photos[name].scale
        original_to_output = (np.diag([solver_to_output_px, solver_to_output_px, 1]) @ to_master[name]
                              @ np.diag([photo_scale / SOLVER_UNIT_PX, photo_scale / SOLVER_UNIT_PX, 1]))
        original_to_output /= original_to_output[2, 2]
        residual = float(np.median([px for _, px in matched_with])) if matched_with else None
        rows.append({"photo": name, "status": "ok", "residual_px": residual, "matched_with": matched_with,
                     "original_to_output": original_to_output.tolist()})

        out_path = out_dir / f"{name}.{args.format}"
        previous_transform = previous.get(name, {}).get("original_to_output")
        unchanged = previous_transform is not None and np.abs(np.array(previous_transform) - original_to_output).max() < 1e-6
        if out_path.exists() and unchanged and not args.rerender:
            continue
        aligned = cv2.warpPerspective(im.read_image(paths[name]), original_to_output, (out_w, out_h), flags=cv2.INTER_LANCZOS4)
        im.save_with_metadata(out_path, aligned, paths[name], quality=args.quality)
        im.write_image(check_dir / f"{name}.jpg", im.make_check_image(aligned, master_image, width=1600), quality=85)
        logger.info(f"{name}: written, residual {'-' if residual is None else f'{residual:.1f}'} px")

    results_file.write_text(json.dumps({row["photo"]: row for row in rows}, indent=1))
    write_report(out_dir, rows, master, warn_px=args.drop_px / 2)
    write_image_index(out_dir)
    failed = [row["photo"] for row in rows if row["status"] != "ok"]
    logger.info(f"done. report: {out_dir / 'report.html'}" + (f"  FAILED: {failed}" if failed else ""))


if __name__ == "__main__":
    main()
