from __future__ import annotations
import random
from typing import List, Tuple, Dict, Any, Optional
from .task import Task

def uunifast(n: int, u_total: float, rng: random.Random) -> List[float]:
    """UUniFast for generating n utilizations that sum to u_total."""
    if n <= 0:
        return []
    sum_u = u_total
    utils = []
    for i in range(1, n):
        next_sum_u = sum_u * (rng.random() ** (1.0 / (n - i)))
        utils.append(sum_u - next_sum_u)
        sum_u = next_sum_u
    utils.append(sum_u)
    return utils

def generate_taskset(
    n_tasks: int,
    n_cores: int,
    target_u_norm: float,
    p_hi_prob: float,
    r_hi_factor: float,
    min_period: int = 1,
    max_period: int = 100,
    n_flags: int = 4,
    seed: Optional[int] = None,
    util_tolerance: float = 0.0,   # if >0, actual u_norm sampled in [u- tol, u+ tol]
) -> Tuple[List[Task], Dict[str, Any]]:
    """
    Generate a mixed-criticality task set consistent with the paper's evaluation section:
      - Total utilization U_total = target_u_norm * m
      - PHI = probability of HI task
      - RHI (here r_hi_factor) in [1..5] acts as multiplier: C_HI = C_LO * RHI for HI tasks
      - LO tasks have C_HI = 0 (dropped in HI mode)
      - Flag identifies interference domain; same flag => interfering tasks.
    """
    rng = random.Random(seed)

    u_norm = target_u_norm
    if util_tolerance and util_tolerance > 0:
        lo = max(0.0, target_u_norm - util_tolerance)
        hi = min(1.0, target_u_norm + util_tolerance)
        u_norm = rng.uniform(lo, hi)

    u_total = u_norm * n_cores
    utils = uunifast(n_tasks, u_total, rng)

    tasks: List[Task] = []
    for i, u_lo in enumerate(utils, start=1):
        crit = "HI" if rng.random() < p_hi_prob else "LO"

        period = rng.randint(min_period, max_period)

        c_lo = u_lo * period
        c_hi = 0.0
        if crit == "HI":
            c_hi = c_lo * r_hi_factor

            # Cap at period to keep utilization <= 1 (simple safeguard)
            if c_hi > period:
                c_hi = float(period)
                c_lo = c_hi / r_hi_factor

        # For LO tasks: c_hi stays 0.0
        flag = rng.randint(1, n_flags)

        tasks.append(Task(task_id=i, criticality=crit, c_lo=float(c_lo), c_hi=float(c_hi), period=int(period), flag=int(flag)))

    meta = {
        "m_cores": n_cores,
        "n_tasks": n_tasks,
        "target_u_norm": target_u_norm,
        "actual_u_norm": u_norm,
        "u_total": u_total,
        "p_hi": p_hi_prob,
        "r_hi": r_hi_factor,
        "n_flags": n_flags,
        "seed": seed,
    }
    return tasks, meta
