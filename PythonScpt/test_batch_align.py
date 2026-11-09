"""Solver check: python PythonScpt/test_batch_align.py

Six fake photos with known transforms to the master, noisy neighbour matches
and one confidently wrong pair: the solver must drop that pair and recover
every photo within 1 px.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import batch_align as ba  # noqa: E402

UNIT = ba.SOLVER_UNIT_PX
rng = np.random.default_rng(1)
names = [str(i) for i in range(6)]
master = "3"


def random_homography():
    angle = np.radians(rng.uniform(-5, 5))
    zoom = rng.uniform(0.95, 1.05)
    return np.array([
        [zoom * np.cos(angle), -zoom * np.sin(angle), rng.uniform(-80, 80)],
        [zoom * np.sin(angle), zoom * np.cos(angle), rng.uniform(-80, 80)],
        [rng.uniform(-2e-5, 2e-5), rng.uniform(-2e-5, 2e-5), 1],
    ])


def apply(H, points):
    projected = np.c_[points, np.ones(len(points))] @ H.T
    return projected[:, :2] / projected[:, 2:]


def ground_points():
    return rng.uniform([0, 0], [2048, 1536], (200, 2))


true_to_master = {name: np.eye(3) if name == master else random_homography() for name in names}
pairs = {}
for i, a in enumerate(names):
    for b in names[i + 1: i + 3]:
        ground = ground_points()
        seen_by_a = apply(np.linalg.inv(true_to_master[a]), ground) + rng.normal(0, 0.7, (200, 2))
        seen_by_b = apply(np.linalg.inv(true_to_master[b]), ground) + rng.normal(0, 0.7, (200, 2))
        pairs[(a, b)] = ba.PhotoPair(seen_by_a / UNIT, seen_by_b / UNIT, match_count=200)

ground = ground_points()
pairs[("0", "5")] = ba.PhotoPair(apply(np.linalg.inv(true_to_master["0"]), ground) / UNIT,
                                 apply(np.linalg.inv(true_to_master["5"]), ground + 60) / UNIT, match_count=50)

solved, _, dropped = ba.solve_dropping_outliers(master, pairs, names, drop_limit=8 / UNIT)
assert [key for key, _ in dropped] == [("0", "5")], f"wrong pair not isolated: {dropped}"

to_px = np.diag([UNIT, UNIT, 1])
grid = np.stack(np.meshgrid(np.linspace(0, 2048, 5), np.linspace(0, 1536, 5)), -1).reshape(-1, 2)
worst = 0.0
for name in names:
    estimated = to_px @ solved[name] @ np.linalg.inv(to_px)
    error = np.linalg.norm(apply(estimated, grid) - apply(true_to_master[name], grid), axis=1).max()
    worst = max(worst, error)
    print(f"photo {name}: max error {error:.2f} px")
assert worst < 1.0, worst
print("OK")
