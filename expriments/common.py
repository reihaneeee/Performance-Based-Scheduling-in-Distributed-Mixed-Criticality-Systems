import csv
import os
from dataclasses import asdict
from typing import Dict, Any, List, Tuple

from src.generator import generate_taskset
from src.fpiap import fpiap_partition
from src.schedulability import schedulable_partitioned
from src.baseline_global import global_schedulable

def save_rows(path: str, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def run_acceptance_curve(
    m: int,
    n_tasks: int,
    util_points: List[float],
    trials_per_point: int,
    p_hi: float,
    r_hi: float,
    n_flags: int,
    V: float = 0.1,
    Tac: float = 0.6,
    seed0: int = 1,
    util_tolerance: float = 0.0,
    min_period: int = 1,
    max_period: int = 100,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Returns:
      - point_results: aggregated per utilization
      - raw_results: per-trial rows (useful for debugging)
    """
    raw_rows: List[Dict[str, Any]] = []
    point_rows: List[Dict[str, Any]] = []

    for ui, u_norm in enumerate(util_points):
        ok_iap = 0
        ok_glob = 0

        for k in range(trials_per_point):
            seed = seed0 + ui * 10_000 + k
            tasks, meta = generate_taskset(
                n_tasks=n_tasks,
                n_cores=m,
                target_u_norm=u_norm,
                p_hi_prob=p_hi,
                r_hi_factor=r_hi,
                min_period=min_period,
                max_period=max_period,
                n_flags=n_flags,
                seed=seed,
                util_tolerance=util_tolerance,
            )

            groups = fpiap_partition(tasks, m=m, V=V)
            iap = schedulable_partitioned(groups, Tac=Tac)
            glob = global_schedulable(tasks, m=m)

            ok_iap += int(iap)
            ok_glob += int(glob)

            raw_rows.append({
                "u_norm": u_norm,
                "trial": k,
                "seed": seed,
                "iap_sched": int(iap),
                "global_sched": int(glob),
                **meta,
            })

        A_iap = ok_iap / trials_per_point
        A_glob = ok_glob / trials_per_point

        point_rows.append({
            "u_norm": u_norm,
            "accept_iap": A_iap,
            "accept_global": A_glob,
            "trials": trials_per_point,
            "m": m,
            "n_tasks": n_tasks,
            "p_hi": p_hi,
            "r_hi": r_hi,
            "n_flags": n_flags,
            "V": V,
            "Tac": Tac,
        })

    return point_rows, raw_rows

def weighted_schedulability(points: List[Dict[str, Any]], key: str) -> float:
    """
    Weighted schedulability per paper (acceptance weighted by utilization):
      AW = sum_u (u * A(u)) / sum_u u
    key: "accept_iap" or "accept_global"
    """
    num = 0.0
    den = 0.0
    for row in points:
        u = float(row["u_norm"])
        a = float(row[key])
        num += u * a
        den += u
    return num / den if den > 0 else 0.0
