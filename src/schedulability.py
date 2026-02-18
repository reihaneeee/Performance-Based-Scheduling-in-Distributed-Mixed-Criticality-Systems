from __future__ import annotations
import math
from typing import List, Dict, Tuple, Optional
from .task import Task
from .fpiap import Group

def mint_for_task(task: Task, groups: List[Group]) -> int:
    """
    Mint: number of other groups/cores where at least one interfering task is running.
    Interference definition: same flag.
    """
    cnt = 0
    for g in groups:
        if any(t.flag == task.flag for t in g.tasks if t.task_id != task.task_id):
            cnt += 1
    # cnt counts groups including own group if it contains another task same flag; we need other cores
    # safer: compute cores that contain at least one task with same flag, excluding the task's own core.
    return max(0, cnt - 1)

def memory_overhead(task: Task, mode: str, mint: int, Tac: float) -> float:
    """
    Additive memory interference latency term.
    Mode in {"LO","HI","MC"}; use AC/RP based on mode WCET.
    """
    if mode == "HI" or mode == "MC":
        return mint * (task.ac_hi + task.rp_hi) * Tac
    return mint * (task.ac_lo + task.rp_lo) * Tac

def rta_fp(task: Task, hp: List[Task], mode: str, mint: int, Tac: float, max_iters: int = 200) -> float:
    """
    Fixed-priority response time analysis on a SINGLE core (partitioned FP).
    mode:
      - "LO": use C_LO of all tasks
      - "HI": use C_HI of HI tasks only
    """
    if mode == "LO":
        C = task.c_lo
        hpC = [(t.period, t.c_lo) for t in hp]
    elif mode == "HI":
        C = task.c_hi
        hpC = [(t.period, t.c_hi) for t in hp if t.criticality == "HI"]
    else:
        raise ValueError("mode must be LO or HI for rta_fp")

    R = C + memory_overhead(task, mode=mode, mint=mint, Tac=Tac)
    for _ in range(max_iters):
        interference = 0.0
        for Tj, Cj in hpC:
            if Cj <= 0:
                continue
            interference += math.ceil(R / Tj) * Cj
        R_next = C + interference + memory_overhead(task, mode=mode, mint=mint, Tac=Tac)
        if R_next == R:
            return R
        if R_next > task.deadline * 10:  # early bailout
            return R_next
        R = R_next
    return R

def rta_mode_change(task_hi: Task, hp_hi: List[Task], hp_lo: List[Task], R_lo_task: float, mint: int, Tac: float, max_iters: int = 200) -> float:
    """
    AMC-like mode-change response time for a HI task.
    Formula (common AMC-rtb style):
      R* = C_i(HI) + sum_{j in hp_HI} ceil(R*/Tj) C_j(HI) + sum_{k in hp_LO} ceil(R_LO_i/Tk) C_k(LO) + mem_overhead(HI)
    """
    C = task_hi.c_hi
    hp_hiC = [(t.period, t.c_hi) for t in hp_hi if t.criticality == "HI"]
    hp_loC = [(t.period, t.c_lo) for t in hp_lo]  # LO-mode carry-in from higher-priority LO/HI tasks

    mem = memory_overhead(task_hi, mode="MC", mint=mint, Tac=Tac)

    R = C + mem
    for _ in range(max_iters):
        inter_hi = 0.0
        for Tj, Cj in hp_hiC:
            if Cj <= 0:
                continue
            inter_hi += math.ceil(R / Tj) * Cj

        inter_lo = 0.0
        for Tk, Ck in hp_loC:
            if Ck <= 0:
                continue
            inter_lo += math.ceil(R_lo_task / Tk) * Ck

        R_next = C + inter_hi + inter_lo + mem
        if R_next == R:
            return R
        if R_next > task_hi.deadline * 10:
            return R_next
        R = R_next
    return R

def audsley_assign(tasks: List[Task], mode: str, groups: List[Group], Tac: float) -> Optional[List[Task]]:
    """
    Audsley's optimal priority assignment:
      - Builds priority list from lowest -> highest.
      - Uses RTA feasibility test that depends only on HP set (not internal ordering).
    Returns list ordered from highest -> lowest priority if feasible, else None.
    """
    remaining = tasks[:]
    assigned_low_to_high: List[Task] = []

    while remaining:
        found = None
        for cand in remaining:
            hp = [t for t in remaining if t != cand]
            mint = mint_for_task(cand, groups)
            R = rta_fp(cand, hp=hp, mode=mode, mint=mint, Tac=Tac)
            if R <= cand.deadline:
                found = cand
                break
        if found is None:
            return None
        remaining.remove(found)
        assigned_low_to_high.append(found)

    # convert to high -> low
    return list(reversed(assigned_low_to_high))

def schedulable_partitioned(groups: List[Group], Tac: float = 0.6) -> bool:
    """
    Algorithm 8-ish schedulability test for partitioned FP (IAP-FP after partitioning):
      1) LO-mode: all tasks on each core must be schedulable (C_LO)
      2) HI-mode: HI tasks on each core schedulable (C_HI), LO tasks dropped
      3) Mode-change: HI tasks meet deadlines under AMC-style bound
    """
    # Quick total util check like paper text
    total_u_lo = sum(t.u_lo for g in groups for t in g.tasks)
    if total_u_lo > len(groups) + 1e-9:
        return False

    # Per-core LO priorities
    core_lo_prio: Dict[int, List[Task]] = {}
    for g in groups:
        pr = audsley_assign(g.tasks, mode="LO", groups=groups, Tac=Tac)
        if pr is None:
            return False
        core_lo_prio[g.gid] = pr
        # check all LO response times explicitly
        for idx, t in enumerate(pr):
            hp = pr[:idx]
            mint = mint_for_task(t, groups)
            R = rta_fp(t, hp=hp, mode="LO", mint=mint, Tac=Tac)
            if R > t.deadline:
                return False

    # HI mode and Mode Change checks for HI tasks only (keep same priorities as LO assignment)
    for g in groups:
        pr_lo = core_lo_prio[g.gid]
        hi_tasks_in_order = [t for t in pr_lo if t.criticality == "HI"]
        if not hi_tasks_in_order:
            continue

        # Precompute R_LO for HI tasks (needed for AMC mode-change formula)
        R_lo_map: Dict[int, float] = {}
        for idx, t in enumerate(pr_lo):
            hp = pr_lo[:idx]
            mint = mint_for_task(t, groups)
            R = rta_fp(t, hp=hp, mode="LO", mint=mint, Tac=Tac)
            if t.criticality == "HI":
                R_lo_map[t.task_id] = R

        # HI-only schedulability
        for idx, t in enumerate(hi_tasks_in_order):
            hp_hi = hi_tasks_in_order[:idx]
            mint = mint_for_task(t, groups)
            R_hi = rta_fp(t, hp=hp_hi, mode="HI", mint=mint, Tac=Tac)
            if R_hi > t.deadline:
                return False

        # Mode-change schedulability
        for idx, t in enumerate(hi_tasks_in_order):
            hp_hi = hi_tasks_in_order[:idx]
            # higher-priority tasks in LO-mode are just all tasks above it in LO priority list
            pos = pr_lo.index(t)
            hp_lo = pr_lo[:pos]
            mint = mint_for_task(t, groups)
            R_mc = rta_mode_change(
                task_hi=t,
                hp_hi=hp_hi,
                hp_lo=hp_lo,
                R_lo_task=R_lo_map.get(t.task_id, t.c_lo),
                mint=mint,
                Tac=Tac,
            )
            if R_mc > t.deadline:
                return False

    return True
