from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from .task import Task

@dataclass
class Group:
    gid: int
    tasks: List[Task]

    @property
    def u_lo(self) -> float:
        return sum(t.u_lo for t in self.tasks)

    @property
    def u_hi(self) -> float:
        return sum(t.u_hi for t in self.tasks if t.criticality == "HI")

    def hi_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.criticality == "HI"]

    def lo_tasks(self) -> List[Task]:
        return [t for t in self.tasks if t.criticality == "LO"]

def dcdusort(tasks: List[Task]) -> List[Task]:
    """
    DCDU: Decreasing Criticality, then Decreasing Utilization.
    Paper sorts HI first, then by utilization (descending).
    We'll use U_HI for HI tasks, U_LO for LO tasks.
    """
    def key(t: Task):
        crit_rank = 0 if t.criticality == "HI" else 1
        util = t.u_hi if t.criticality == "HI" else t.u_lo
        return (crit_rank, -util)
    return sorted(tasks, key=key)

def allocate_dcdu_wf(tasks: List[Task], m: int) -> List[Group]:
    """
    Algorithm 1: DCDU-WF allocation to m groups.
    - allocate HI tasks to group with smallest used U^HI (worst-fit free space)
    - then allocate LO tasks to group with smallest used U^LO
    """
    groups = [Group(gid=i, tasks=[]) for i in range(m)]
    ordered = dcdusort(tasks)

    # HI first
    for t in [x for x in ordered if x.criticality == "HI"]:
        g = min(groups, key=lambda gg: gg.u_hi)
        g.tasks.append(t)

    # LO next
    for t in [x for x in ordered if x.criticality == "LO"]:
        g = min(groups, key=lambda gg: gg.u_lo)
        g.tasks.append(t)

    return groups

def flag_count(group: Group, flag: int, crit: Optional[str] = None) -> int:
    """Algorithm 2: count tasks with a specific flag in a group (optionally only HI/LO)."""
    if crit is None:
        return sum(1 for t in group.tasks if t.flag == flag)
    return sum(1 for t in group.tasks if t.flag == flag and t.criticality == crit)

def _find_groups_by_flag(groups: List[Group], flag: int, crit: str) -> Tuple[Group, Group, int, int]:
    counts = [(g, flag_count(g, flag, crit=crit)) for g in groups]
    max_g, max_c = max(counts, key=lambda x: x[1])
    min_g, min_c = min(counts, key=lambda x: x[1])
    return max_g, min_g, max_c, min_c

def swap_hi_by_flags(groups: List[Group], V: float = 0.1) -> None:
    """
    Algorithms 3-4 (HI mode swapping).
    Goal: balance distribution of HI tasks with the same flag across groups,
    while keeping each group's HI utilization <= 1 and utilization difference <= V.
    """
    if not groups:
        return
    all_flags = sorted({t.flag for g in groups for t in g.hi_tasks()})
    if not all_flags:
        return

    for f in all_flags:
        changed = True
        safety = 0
        while changed and safety < 200:
            safety += 1
            max_g, min_g, max_c, min_c = _find_groups_by_flag(groups, f, crit="HI")
            changed = False
            if max_c - min_c <= 1:
                break  # already balanced enough

            # candidates: HI tasks with flag f in max_g
            cand_max = [t for t in max_g.hi_tasks() if t.flag == f]
            # candidates in min_g: any HI task (prefer different flag to reduce max_c)
            cand_min = [t for t in min_g.hi_tasks() if t.flag != f] or min_g.hi_tasks()
            if not cand_max or not cand_min:
                break

            # try swaps greedily
            best_pair = None
            best_delta = None
            for t_from_max in cand_max:
                for t_from_min in cand_min:
                    new_u_max = max_g.u_hi - t_from_max.u_hi + t_from_min.u_hi
                    new_u_min = min_g.u_hi - t_from_min.u_hi + t_from_max.u_hi
                    if new_u_max >= 1.0 or new_u_min >= 1.0:
                        continue
                    if abs(new_u_max - new_u_min) > V:
                        continue
                    # improvement: reduce (max_count - min_count)
                    new_max_c = max_c - 1 + (1 if t_from_min.flag == f else 0)
                    new_min_c = min_c + 1 - (1 if t_from_min.flag == f else 0)
                    delta = (max_c - min_c) - (new_max_c - new_min_c)
                    if delta <= 0:
                        continue
                    if best_delta is None or delta > best_delta:
                        best_delta = delta
                        best_pair = (t_from_max, t_from_min)

            if best_pair:
                a, b = best_pair
                max_g.tasks.remove(a)
                min_g.tasks.remove(b)
                max_g.tasks.append(b)
                min_g.tasks.append(a)
                changed = True

def balance_lo_utilization(groups: List[Group]) -> None:
    """
    Algorithm 5 (LO mode utilization balancing).
    Rebalances LO utilization across groups by swapping the largest-ULO task from the
    most-loaded group with a smallest-ULO task from least-loaded group (heuristic).
    """
    if not groups:
        return
    avg = sum(g.u_lo for g in groups) / len(groups)

    active = [g for g in groups if not (avg * 0.95 <= g.u_lo <= avg * 1.05)]
    if len(active) < 2:
        return

    # perform a few balancing steps
    for _ in range(50):
        max_g = max(active, key=lambda g: g.u_lo)
        min_g = min(active, key=lambda g: g.u_lo)

        max_lo_tasks = max_g.lo_tasks()
        min_lo_tasks = min_g.lo_tasks()
        if not max_lo_tasks or not min_lo_tasks:
            break

        t_big = max(max_lo_tasks, key=lambda t: t.u_lo)
        t_small = min(min_lo_tasks, key=lambda t: t.u_lo)

        new_u_max = max_g.u_lo - t_big.u_lo + t_small.u_lo
        new_u_min = min_g.u_lo - t_small.u_lo + t_big.u_lo
        if new_u_max < 1.0 and new_u_min < 1.0 and (new_u_max - new_u_min) < (max_g.u_lo - min_g.u_lo):
            max_g.tasks.remove(t_big)
            min_g.tasks.remove(t_small)
            max_g.tasks.append(t_small)
            min_g.tasks.append(t_big)
        else:
            break

def swap_lo_by_flags(groups: List[Group], V: float = 0.1) -> None:
    """
    Algorithms 6-7 (LO mode swapping based on flags).
    Balance LO tasks with the same flag across groups, while keeping each group's
    LO utilization <= 1 and utilization difference <= V.
    """
    if not groups:
        return
    all_flags = sorted({t.flag for g in groups for t in g.lo_tasks()})
    if not all_flags:
        return

    for f in all_flags:
        changed = True
        safety = 0
        while changed and safety < 200:
            safety += 1
            max_g, min_g, max_c, min_c = _find_groups_by_flag(groups, f, crit="LO")
            changed = False
            if max_c - min_c <= 1:
                break

            cand_max = [t for t in max_g.lo_tasks() if t.flag == f]
            cand_min = [t for t in min_g.lo_tasks() if t.flag != f] or min_g.lo_tasks()
            if not cand_max or not cand_min:
                break

            best_pair = None
            best_delta = None
            for t_from_max in cand_max:
                for t_from_min in cand_min:
                    new_u_max = max_g.u_lo - t_from_max.u_lo + t_from_min.u_lo
                    new_u_min = min_g.u_lo - t_from_min.u_lo + t_from_max.u_lo
                    if new_u_max >= 1.0 or new_u_min >= 1.0:
                        continue
                    if abs(new_u_max - new_u_min) > V:
                        continue
                    new_max_c = max_c - 1 + (1 if t_from_min.flag == f else 0)
                    new_min_c = min_c + 1 - (1 if t_from_min.flag == f else 0)
                    delta = (max_c - min_c) - (new_max_c - new_min_c)
                    if delta <= 0:
                        continue
                    if best_delta is None or delta > best_delta:
                        best_delta = delta
                        best_pair = (t_from_max, t_from_min)

            if best_pair:
                a, b = best_pair
                max_g.tasks.remove(a)
                min_g.tasks.remove(b)
                max_g.tasks.append(b)
                min_g.tasks.append(a)
                changed = True

def fpiap_partition(tasks: List[Task], m: int, V: float = 0.1) -> List[Group]:
    """
    Full FP-IAP allocation pipeline:
      1) Algorithm 1: DCDU-WF initial allocation
      2) Algorithms 3-4: swap HI tasks by flags
      3) Algorithm 5: balance LO utilization
      4) Algorithms 6-7: swap LO tasks by flags
    """
    groups = allocate_dcdu_wf(tasks, m)
    swap_hi_by_flags(groups, V=V)
    balance_lo_utilization(groups)
    swap_lo_by_flags(groups, V=V)
    return groups
