from __future__ import annotations
import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from .task import Task

@dataclass
class Job:
    task: Task
    release: int
    deadline: int
    remaining: int

def _priority_key(task: Task) -> Tuple[int, float]:
    """
    Global fixed priority: DCDU (HI first, then higher utilization).
    """
    crit_rank = 0 if task.criticality == "HI" else 1
    util = task.u_hi if task.criticality == "HI" else task.u_lo
    return (crit_rank, -util)

def simulate_global_fp(
    tasks: List[Task],
    m: int,
    horizon: int,
    mode: str = "LO",
    time_unit: float = 1.0,
) -> bool:
    """
    Discrete-time preemptive Global Fixed Priority simulation.
    - mode "LO": all tasks, execution = C_LO
    - mode "HI": only HI tasks, execution = C_HI
    Uses integer time (ticks). Execution times are rounded up to ticks.
    """
    if mode == "HI":
        tasks = [t for t in tasks if t.criticality == "HI" and t.c_hi > 0]

    # Precompute per-task execution in ticks
    exec_ticks: Dict[int, int] = {}
    for t in tasks:
        C = t.c_lo if mode == "LO" else t.c_hi
        exec_ticks[t.task_id] = max(1, int(math.ceil(C / time_unit))) if C > 0 else 0

    # Fixed task priorities
    ordered = sorted(tasks, key=_priority_key)

    active: List[Job] = []
    for t in range(horizon + 1):
        # release jobs
        for task in ordered:
            if task.period <= 0:
                continue
            if t % task.period == 0:
                c = exec_ticks[task.task_id]
                if c > 0:
                    active.append(Job(task=task, release=t, deadline=t + task.deadline, remaining=c))

        # deadline check at time t
        for j in list(active):
            if t >= j.deadline and j.remaining > 0:
                return False

        # choose up to m jobs by priority (task priority, then earliest deadline)
        active.sort(key=lambda j: (_priority_key(j.task), j.deadline))
        running = active[:m]

        # execute one tick
        for j in running:
            j.remaining -= 1

        # remove completed
        active = [j for j in active if j.remaining > 0]

    return True

def global_schedulable(tasks: List[Task], m: int, horizon_factor: int = 10, time_unit: float = 1.0) -> bool:
    """
    Baseline acceptance:
      - LO mode schedulable (all tasks with C_LO)
      - HI mode schedulable (HI tasks with C_HI)
    Horizon = horizon_factor * max_period (simple cap to keep runtime reasonable).
    """
    max_p = max(t.period for t in tasks) if tasks else 0
    horizon = max(1, horizon_factor * max_p)

    if not simulate_global_fp(tasks, m=m, horizon=horizon, mode="LO", time_unit=time_unit):
        return False
    if not simulate_global_fp(tasks, m=m, horizon=horizon, mode="HI", time_unit=time_unit):
        return False
    return True
